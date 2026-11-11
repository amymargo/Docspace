#!/usr/bin/env python3
"""Tiny collaborative document editor using only Python's standard library."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path
import json, sqlite3, uuid, html, os

ROOT = Path(__file__).parent
DB = Path(os.environ.get('DOCS_DB', ROOT / 'documents.db'))


def connect():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys = ON')
    return db


def init_db():
    with connect() as db:
        db.executescript('''
        CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL);
        CREATE TABLE IF NOT EXISTS documents(id TEXT PRIMARY KEY, title TEXT NOT NULL, content TEXT NOT NULL DEFAULT '', owner_id TEXT NOT NULL REFERENCES users(id), created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS shares(document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE, user_id TEXT NOT NULL REFERENCES users(id), PRIMARY KEY(document_id,user_id));
        ''')
        cols={r['name'] for r in db.execute('PRAGMA table_info(documents)')}
        if 'created_at' not in cols: db.execute("ALTER TABLE documents ADD COLUMN created_at TEXT NOT NULL DEFAULT ''")
        if 'created_at' not in cols: db.execute("UPDATE documents SET created_at=updated_at WHERE created_at=''")
        db.executemany('INSERT OR IGNORE INTO users(id,name,email) VALUES(?,?,?)', [('amy','Amy Margolina','amy@example.com'),('alex','Alex Rivera','alex@example.com'),('sam','Sam Chen','sam@example.com')])


def json_body(handler):
    n = int(handler.headers.get('Content-Length', 0))
    if n > 15_000_000: raise ValueError('Request is too large (2 MB limit).')
    return json.loads(handler.rfile.read(n) or b'{}')

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(ROOT/'static'),**kwargs)
    def send_json(self, value, status=200):
        body=json.dumps(value).encode(); self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)
    def current_user(self):
        uid=self.headers.get('X-User-Id','amy')
        with connect() as db: return db.execute('SELECT * FROM users WHERE id=?',(uid,)).fetchone()
    def allowed(self, doc, user):
        if not doc or not user: return False
        with connect() as db: return doc['owner_id']==user['id'] or db.execute('SELECT 1 FROM shares WHERE document_id=? AND user_id=?',(doc['id'],user['id'])).fetchone() is not None
    def do_GET(self):
        p=urlparse(self.path); user=self.current_user()
        if p.path=='/api/users':
            with connect() as db: return self.send_json([dict(x) for x in db.execute('SELECT id,name,email FROM users')])
        if p.path=='/api/docs':
            if not user: return self.send_json({'error':'Unknown user.'},401)
            with connect() as db:
                rows=db.execute('''SELECT d.*,u.name owner_name, CASE WHEN d.owner_id=? THEN 'owned' ELSE 'shared' END access FROM documents d JOIN users u ON u.id=d.owner_id WHERE d.owner_id=? OR EXISTS(SELECT 1 FROM shares s WHERE s.document_id=d.id AND s.user_id=?) ORDER BY d.updated_at DESC''',(user['id'],user['id'],user['id'])).fetchall()
                return self.send_json([dict(x) for x in rows])
        if p.path.startswith('/api/docs/'):
            did=p.path.split('/')[-1]
            with connect() as db: doc=db.execute('SELECT d.*,u.name owner_name FROM documents d JOIN users u ON u.id=d.owner_id WHERE d.id=?',(did,)).fetchone()
            if not self.allowed(doc,user): return self.send_json({'error':'Document not found or access denied.'},404)
            with connect() as db: shares=[dict(x) for x in db.execute('SELECT u.id,u.name,u.email FROM shares s JOIN users u ON u.id=s.user_id WHERE s.document_id=?',(did,))]
            return self.send_json({**dict(doc),'shares':shares,'can_edit': True, 'can_manage': doc['owner_id']==user['id']})
        return super().do_GET()
    def do_POST(self):
        p=urlparse(self.path); user=self.current_user()
        try: data=json_body(self)
        except (ValueError,json.JSONDecodeError) as e: return self.send_json({'error':str(e)},400)
        if not user: return self.send_json({'error':'Unknown user.'},401)
        if p.path=='/api/docs':
            title=str(data.get('title') or 'Untitled document').strip()[:120] or 'Untitled document'; did=uuid.uuid4().hex
            with connect() as db: db.execute("INSERT INTO documents(id,title,content,owner_id,created_at,updated_at) VALUES(?,?,?,?,strftime('%Y-%m-%d %H:%M:%f','now'),strftime('%Y-%m-%d %H:%M:%f','now'))",(did,title,str(data.get('content','')),user['id']))
            return self.send_json({'id':did,'title':title},201)
        if p.path.startswith('/api/docs/') and p.path.endswith('/share'):
            did=p.path.split('/')[-2]
            with connect() as db:
                doc=db.execute('SELECT * FROM documents WHERE id=?',(did,)).fetchone()
                if not doc or doc['owner_id']!=user['id']: return self.send_json({'error':'Only the owner can share this document.'},403)
                target=db.execute('SELECT * FROM users WHERE email=? OR id=?',(str(data.get('email','')).strip().lower(),str(data.get('email','')).strip())).fetchone()
                if not target: return self.send_json({'error':'No seeded user found for that email.'},404)
                if target['id']==user['id']: return self.send_json({'error':'You already own this document.'},400)
                db.execute('INSERT OR IGNORE INTO shares(document_id,user_id) VALUES(?,?)',(did,target['id']))
            return self.send_json({'ok':True,'name':target['name']})
        return self.send_json({'error':'Not found.'},404)
    def do_PUT(self):
        p=urlparse(self.path); user=self.current_user()
        try: data=json_body(self)
        except (ValueError,json.JSONDecodeError) as e: return self.send_json({'error':str(e)},400)
        did=p.path.split('/')[-1]
        with connect() as db:
            doc=db.execute('SELECT * FROM documents WHERE id=?',(did,)).fetchone()
            if not self.allowed(doc,user): return self.send_json({'error':'Document not found or access denied.'},404)
            is_owner=doc['owner_id']==user['id']
            title=(str(data.get('title',doc['title'])).strip()[:120] or 'Untitled document') if is_owner else doc['title']; content=str(data.get('content',doc['content']))
            if len(content)>14_000_000: return self.send_json({'error':'Document content exceeds 14 MB.'},413)
            db.execute("UPDATE documents SET title=?,content=?,updated_at=strftime('%Y-%m-%d %H:%M:%f','now') WHERE id=?",(title,content,did))
        return self.send_json({'ok':True})
    def do_DELETE(self):
        p=urlparse(self.path); user=self.current_user(); bits=p.path.strip('/').split('/')
        if not user or len(bits)<3 or bits[0]!='api' or bits[1]!='docs': return self.send_json({'error':'Not found.'},404)
        did=bits[2]
        with connect() as db:
            doc=db.execute('SELECT * FROM documents WHERE id=?',(did,)).fetchone()
            if not doc: return self.send_json({'error':'Document not found.'},404)
            if len(bits)==3:
                if doc['owner_id']!=user['id']:
                    db.execute('DELETE FROM shares WHERE document_id=? AND user_id=?',(did,user['id'])); return self.send_json({'ok':True})
                db.execute('DELETE FROM documents WHERE id=?',(did,)); return self.send_json({'ok':True})
            if len(bits)==5 and bits[3]=='share':
                target=bits[4]
                if user['id']!=doc['owner_id'] and user['id']!=target: return self.send_json({'error':'Access denied.'},403)
                db.execute('DELETE FROM shares WHERE document_id=? AND user_id=?',(did,target)); return self.send_json({'ok':True})
        return self.send_json({'error':'Not found.'},404)
    def log_message(self,fmt,*args): print('%s - %s'%(self.address_string(),fmt%args))

if __name__=='__main__':
    init_db(); port=int(os.environ.get('PORT','8000')); print(f'Docspace running at http://localhost:{port}'); ThreadingHTTPServer(('0.0.0.0',port),Handler).serve_forever()
