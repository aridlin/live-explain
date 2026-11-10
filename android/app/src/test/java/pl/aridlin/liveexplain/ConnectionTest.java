package pl.aridlin.liveexplain;
import org.junit.Test;
import static org.junit.Assert.*;
public class ConnectionTest {
    @Test public void acceptsLocalAddressWithoutCode() {
        Connection c=new Connection("192.168.0.39");
        assertEquals("192.168.0.39",c.host);assertEquals(8080,c.port);
        assertEquals("http://192.168.0.39:8080",c.address);
        assertEquals(8766,new Connection("http://10.0.2.2:8766/").port);
    }
    @Test public void acceptsPortalAndPresenterUrls() {
        Connection c=new Connection("https://prol.aridlin.pl/live-explain/","aridlin","password");
        assertTrue(c.secure);assertEquals(443,c.port);
        assertEquals("https://prol.aridlin.pl/live-explain",c.address);
        assertEquals(c.address,new Connection("https://prol.aridlin.pl/live-explain/presenter/").address);
        assertEquals("https://example.org:8443",new Connection("https://example.org:8443/").address);
    }
    @Test public void neverAcceptsCredentialsInUrlsOrCleartext() {
        assertThrows(Exception.class,()->new Connection("http://192.168.0.39","user","secret"));
        for(String value:new String[]{"https://u:p@example.org/","https://example.org/a/../b","https://example.org/%2e%2e/","https://example.org/?secret=x"})
            assertThrows(value,Exception.class,()->new Connection(value));
    }
    @Test public void rejectsInvalidAddressesAndOldPairingLinks() {
        for(String input:new String[]{"", "256.1.1.1", "1.2.3", "http://1.2.3.4:99999", "http://u:p@1.2.3.4", "http://1.2.3.4/a", "liveexplain://pair?host=1.2.3.4"})
            assertThrows(input,Exception.class,()->new Connection(input));
    }
}
