"""Transport-independent controller boundary; no network listener in this milestone."""

from copy import deepcopy
import hmac
import json
import secrets


class CommandHost:
    ALLOWED = {
        "advance",
        "pause",
        "freeze",
        "play",
        "step",
        "finish",
        "replay",
        "return",
        "undo",
        "detour",
        "depth",
    }

    def __init__(self, session):
        self.session = session
        self.token = secrets.token_urlsafe(32)
        self.receipts = {}
        self.controller = None

    def handle(self, raw, token, controller="phone"):
        if not isinstance(token, str) or not hmac.compare_digest(token, self.token):
            return {"status": "unauthorized"}
        if self.controller not in (None, controller):
            return {"status": "unauthorized"}
        if not isinstance(raw, str) or len(raw.encode()) > 4096:
            return {"status": "invalid"}
        try:
            value = json.loads(raw)
            if not isinstance(value, dict) or set(value) != {"epoch", "id", "revision", "kind", "value"}:
                return {"status": "invalid"}
            if (
                not isinstance(value["id"], str)
                or not 1 <= len(value["id"]) <= 128
                or type(value["revision"]) is not int
                or value["kind"] not in self.ALLOWED
                or value["value"] is not None
                and not isinstance(value["value"], str)
            ):
                return {"status": "invalid"}
        except (ValueError, TypeError):
            return {"status": "invalid"}
        if value["epoch"] != self.session.epoch:
            return {"status": "wrong_epoch", "state": self.session.controller_state()}
        self.controller = controller
        key = (self.session.epoch, controller, value["id"])
        if key in self.receipts:
            receipt, original = self.receipts[key]
            if value != original:
                return {"status": "id_conflict"}
            return deepcopy(receipt)
        accepted, message = self.session.command(value["kind"], value["value"], value["revision"])
        receipt = dict(
            status="accepted" if accepted else "rejected",
            id=value["id"],
            message=message,
            state=self.session.controller_state(),
        )
        self.receipts[key] = (deepcopy(receipt), value)
        return receipt

    def synchronize(self, token):
        if not isinstance(token, str) or not hmac.compare_digest(token, self.token):
            raise PermissionError("Unauthorized")
        return self.session.controller_state()
