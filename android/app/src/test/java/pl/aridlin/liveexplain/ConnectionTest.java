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
    @Test public void rejectsInvalidAddressesAndOldPairingLinks() {
        for(String input:new String[]{"", "256.1.1.1", "1.2.3", "http://1.2.3.4:99999", "https://1.2.3.4", "http://u:p@1.2.3.4", "http://1.2.3.4/a", "liveexplain://pair?host=1.2.3.4"})
            assertThrows(input,Exception.class,()->new Connection(input));
    }
}
