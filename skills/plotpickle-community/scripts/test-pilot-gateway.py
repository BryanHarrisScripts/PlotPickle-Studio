import importlib.util, unittest
from pathlib import Path
p = Path(__file__).with_name("pilot-gateway.py")
spec = importlib.util.spec_from_file_location("pilot_gateway",p)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
class PilotTests(unittest.TestCase):
    def test_four_rooms_exact(self):
        self.assertEqual([r["name"] for r in mod.load()["rooms"]],["HOME","CHAT","ELARA","SHOW"])
    def test_no_false_live_status(self):
        self.assertFalse(mod.prepare("preview")["liveChat"])
        self.assertEqual(mod.prepare("preview")["status"],"pilot-prepared-not-deployed")
    def test_invite_only_draft(self):
        d=mod.prepare("request-intent")
        self.assertFalse(d["inviteSent"])
        self.assertFalse(d["credentialsRequested"])
        self.assertFalse(d["joinCompleted"])
    def test_live_validation_required(self):
        self.assertFalse(mod.prepare("acceptance")["allPassed"])
if __name__ == "__main__":unittest.main()
