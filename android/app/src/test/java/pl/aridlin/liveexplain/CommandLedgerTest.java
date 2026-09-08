package pl.aridlin.liveexplain;
import org.junit.Test;
import org.json.JSONObject;
import static org.junit.Assert.*;

public class CommandLedgerTest {
    private JSONObject state() throws Exception { return new JSONObject("{\"epoch\":\"talk\",\"revision\":7}"); }
    @Test public void processRestartPreservesExactEnvelope() throws Exception {
        CommandLedger ledger=new CommandLedger("");
        String original=ledger.begin(state(),"advance",null);
        assertEquals(original,new CommandLedger(original).pending());
    }
    @Test public void secondTapCannotCreateBacklog() throws Exception {
        CommandLedger ledger=new CommandLedger(""); ledger.begin(state(),"advance",null);
        assertThrows(IllegalStateException.class,()->ledger.begin(state(),"advance",null));
    }
    @Test public void unrelatedAckDoesNotReleasePending() throws Exception {
        CommandLedger ledger=new CommandLedger(""); ledger.begin(state(),"advance",null);
        assertFalse(ledger.receive(new JSONObject("{\"status\":\"accepted\",\"id\":\"other\"}")));
        assertFalse(ledger.pending().isEmpty());
    }
    @Test public void receiptReleasesExactlyOnePending() throws Exception {
        CommandLedger ledger=new CommandLedger(""); JSONObject envelope=new JSONObject(ledger.begin(state(),"advance",null));
        JSONObject ack=new JSONObject().put("status","accepted").put("id",envelope.getString("id"));
        assertTrue(ledger.receive(ack)); assertEquals("",ledger.pending()); assertFalse(ledger.receive(ack));
    }
    @Test public void newEpochDropsObsoleteCommand() throws Exception {
        CommandLedger ledger=new CommandLedger(""); ledger.begin(state(),"advance",null);
        assertTrue(ledger.receive(new JSONObject("{\"status\":\"wrong_epoch\"}")));
        assertEquals("",ledger.pending());
    }
    @Test public void pendingServerResultDoesNotAllowNextTap() throws Exception {
        CommandLedger ledger=new CommandLedger(""); ledger.begin(state(),"advance",null);
        assertFalse(ledger.receive(new JSONObject("{\"status\":\"pending\"}")));
    }
}
