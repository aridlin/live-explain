package pl.aridlin.liveexplain;
import org.junit.Test;
import static org.junit.Assert.*;
public class ConnectionTest {
    @Test public void discoveryCannotChangeTrustIdentity() throws Exception {
        String pin="a".repeat(64);
        Connection c=new Connection("liveexplain://pair?host=127.0.0.1&port=8765&pin="+pin+"&token="+"b".repeat(43));
        assertNull(c.relocated("192.168.1.4",8765,"c".repeat(64)));
        String uri=c.relocated("192.168.1.4",8765,pin);
        assertNotNull(uri);assertEquals(pin,new Connection(uri).pin);
        assertEquals(c.token,new Connection(uri).token);
    }
    @Test public void rejectsWebLinksAndIncompletePairing() {
        assertThrows(Exception.class,()->new Connection("https://example.com"));
        assertThrows(Exception.class,()->new Connection("liveexplain://pair?host=127.0.0.1"));
    }
}
