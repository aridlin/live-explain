"""Authenticated commands with revision checks and session-lifetime retry receipts."""

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
        "blank",
        "output",
    }

    def __init__(self, session, dispatch=None, state=None):
        self.session = session
        self.dispatch = dispatch or session.command
        self.state = state or session.controller_state
        self.token = secrets.token_urlsafe(32)
        self.receipts = {}
        self.controller = None

    def handle(self, raw, token, controller="phone", resolve=False):
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
            return {"status": "wrong_epoch", "state": self.state()}
        self.controller = controller
        key = (self.session.epoch, controller, value["id"])
        if key in self.receipts:
            receipt, original = self.receipts[key]
            if value != original:
                return {"status": "id_conflict"}
            return deepcopy(receipt)
        if resolve:
            accepted, message = False, "Polecenie nie dotarło; anulowano spóźnione wykonanie."
        elif value["revision"] != self.session.revision:
            accepted, message = False, "Nieaktualny stan sterowania."
        elif len(self.receipts) >= 20000:
            accepted, message = False, "Limit poleceń sesji."
        else:
            accepted, message = self.dispatch(value["kind"], value["value"])

        receipt = dict(
            status="accepted" if accepted else "rejected",
            id=value["id"],
            message=message,
            state=self.state(),
        )
        if len(self.receipts) < 20000:
            self.receipts[key] = (deepcopy(receipt), value)
        return receipt

    def synchronize(self, token):
        if not isinstance(token, str) or not hmac.compare_digest(token, self.token):
            raise PermissionError("Unauthorized")
        return self.state()
