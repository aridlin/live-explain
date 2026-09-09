package pl.aridlin.liveexplain;

import org.json.JSONObject;
import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;

/** Direct local HTTP transport. No pairing code, token or certificate enrollment. */
final class Connection {
    final String host, address;
    final int port;
    Connection(String value) {
        String raw=value.trim();
        URI uri=URI.create(raw.contains("://")?raw:"http://"+raw);
        host=uri.getHost(); port=uri.getPort()==-1?8080:uri.getPort();
        if(!"http".equals(uri.getScheme()) || host==null || uri.getUserInfo()!=null
                || uri.getRawQuery()!=null || uri.getRawFragment()!=null || port<1 || port>65535
                || !(uri.getPath().isEmpty() || uri.getPath().equals("/")))
            throw new IllegalArgumentException("Wpisz adres IP laptopa, opcjonalnie z portem.");
        String[] octets=host.split("\\.",-1);
        if(octets.length!=4)throw new IllegalArgumentException("Wpisz adres IPv4 laptopa.");
        for(String octet:octets)if(!octet.matches("[0-9]{1,3}") || Integer.parseInt(octet)>255)
            throw new IllegalArgumentException("Nieprawidłowy adres IPv4.");
        address="http://"+host+":"+port;
    }
    JSONObject request(String command, String controller, boolean resolve) throws Exception {
        HttpURLConnection c=(HttpURLConnection)new URL("http",host,port,
                command==null?"/state":resolve?"/resolve":"/command").openConnection();
        c.setConnectTimeout(2500); c.setReadTimeout(5500); c.setInstanceFollowRedirects(false);
        c.setRequestProperty("X-Controller",controller);
        try {
            if(command!=null) {
                c.setRequestMethod("POST");c.setDoOutput(true);
                byte[] bytes=command.getBytes(StandardCharsets.UTF_8);
                c.setFixedLengthStreamingMode(bytes.length);c.setRequestProperty("Content-Type","application/json");
                try(OutputStream out=c.getOutputStream()){out.write(bytes);}
            }
            int status=c.getResponseCode();
            if(status!=200)throw new IOException("Laptop odpowiedział HTTP "+status);
            try(InputStream in=c.getInputStream();ByteArrayOutputStream out=new ByteArrayOutputStream()) {
                byte[] buffer=new byte[4096];int n;
                while((n=in.read(buffer))!=-1) {
                    if(out.size()+n>262144)throw new IOException("Odpowiedź zbyt duża");
                    out.write(buffer,0,n);
                }
                return new JSONObject(out.toString("UTF-8"));
            }
        } finally {c.disconnect();}
    }
}
