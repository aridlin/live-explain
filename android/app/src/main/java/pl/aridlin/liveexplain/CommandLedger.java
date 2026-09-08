package pl.aridlin.liveexplain;

import org.json.JSONObject;
import org.json.JSONException;
import java.util.UUID;

/** One durable pending command. A retry always uses the exact original envelope. */
final class CommandLedger {
    private JSONObject pending;
    CommandLedger(String saved) throws JSONException {
        if (saved != null && !saved.isEmpty()) pending = new JSONObject(saved);
    }
    synchronized String pending() { return pending == null ? "" : pending.toString(); }
    synchronized String begin(JSONObject state, String kind, String value) throws JSONException {
        if (pending != null) throw new IllegalStateException("Command still awaiting receipt");
        pending = new JSONObject().put("epoch", state.getString("epoch"))
                .put("revision", state.getLong("revision")).put("id", UUID.randomUUID().toString())
                .put("kind", kind).put("value", value == null ? JSONObject.NULL : value);
        return pending.toString();
    }
    synchronized boolean receive(JSONObject response) {
        if (pending == null) return false;
        String status = response.optString("status");
        boolean matching = pending.optString("id").equals(response.optString("id"));
        if ((matching && (status.equals("accepted") || status.equals("rejected")))
                || status.equals("wrong_epoch") || status.equals("id_conflict")) {
            pending = null;
            return true;
        }
        return false;
    }
}
