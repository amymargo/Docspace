import io, json, tempfile, unittest
from pathlib import Path
import server

class FakeHandler(server.Handler):
    """Call the real API handlers without opening a network socket."""
    def __init__(self, path, user='amy', payload=None):
        self.path=path; self.headers={'X-User-Id':user,'Content-Length':str(len(json.dumps(payload or {}).encode()))}
        self.rfile=io.BytesIO(json.dumps(payload or {}).encode()); self.response=None
    def send_json(self,value,status=200): self.response=(status,value)
    def log_message(self,*args): pass

def call(method,path,user='amy',payload=None):
    handler=FakeHandler(path,user,payload); getattr(handler,method)(); return handler.response

class DocumentRulesTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.old_db=server.DB; server.DB=Path(self.tmp.name)/'test.sqlite'; server.init_db()
    def tearDown(self): server.DB=self.old_db; self.tmp.cleanup()
    def test_migrates_existing_database(self):
        with server.connect() as db:
            db.execute('DROP TABLE shares'); db.execute('DROP TABLE documents')
            db.execute("CREATE TABLE documents(id TEXT PRIMARY KEY,title TEXT NOT NULL,content TEXT NOT NULL DEFAULT '',owner_id TEXT NOT NULL,updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
            db.execute("INSERT INTO documents(id,title,owner_id,updated_at) VALUES('legacy','Old','amy','2026-01-02 03:04:05')")
        server.init_db()
        with server.connect() as db: self.assertEqual(db.execute("SELECT created_at FROM documents WHERE id='legacy'").fetchone()['created_at'],'2026-01-02 03:04:05')
    def test_create_persist_share_visibility_and_read_only_boundary(self):
        status,created=call('do_POST','/api/docs',payload={'title':'Planning','content':'<p>Draft</p>'})
        self.assertEqual(status,201); did=created['id']
        self.assertEqual(call('do_GET','/api/docs/'+did,'amy')[0],200)
        self.assertEqual(call('do_GET','/api/docs/'+did,'alex')[0],404)
        self.assertEqual(call('do_POST',f'/api/docs/{did}/share','amy',{'email':'alex'})[0],200)
        status,opened=call('do_GET','/api/docs/'+did,'alex')
        self.assertEqual(status,200); self.assertEqual(opened['content'],'<p>Draft</p>'); self.assertTrue(opened['can_edit'])
        self.assertEqual(call('do_PUT','/api/docs/'+did,'alex',{'title':'Renamed by Alex','content':'<p>Collaborative edit</p>'})[0],200)
        shared_edit=call('do_GET','/api/docs/'+did,'amy')[1]; self.assertEqual(shared_edit['content'],'<p>Collaborative edit</p>'); self.assertEqual(shared_edit['title'],'Planning')
        self.assertEqual(call('do_PUT','/api/docs/'+did,'amy',{'content':'<p>Revised</p>'})[0],200)
        self.assertEqual(call('do_GET','/api/docs/'+did,'amy')[1]['content'],'<p>Revised</p>')
        self.assertEqual(call('do_DELETE',f'/api/docs/{did}/share/alex','amy')[0],200)
        self.assertEqual(call('do_GET','/api/docs/'+did,'alex')[0],404)
        self.assertEqual(call('do_POST',f'/api/docs/{did}/share','amy',{'email':'alex'})[0],200)
        self.assertEqual(call('do_DELETE','/api/docs/'+did,'alex')[0],200)
        self.assertEqual(call('do_GET','/api/docs/'+did,'alex')[0],404)
        self.assertEqual(call('do_DELETE','/api/docs/'+did,'amy')[0],200)
        self.assertEqual(call('do_GET','/api/docs/'+did,'amy')[0],404)

if __name__=='__main__': unittest.main()
