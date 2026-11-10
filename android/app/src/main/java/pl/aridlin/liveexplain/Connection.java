package pl.aridlin.liveexplain;

import org.json.JSONObject;
import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.util.Base64;

/** LAN HTTP or portal HTTPS; credentials stay in memory and are sent only over TLS. */
final class Connection {
    final String host, address;
    final int port;
    final boolean secure;
    private final String authorization;
    Connection(String value) { this(value,"",""); }
    Connection(String value,String username,String password) {
        String raw=value.trim();
        URI uri=URI.create(raw.contains("://")?raw:"http://"+raw);
        secure="https".equalsIgnoreCase(uri.getScheme());
        host=uri.getHost(); port=uri.getPort()==-1?(secure?443:8080):uri.getPort();
        String path=uri.getRawPath();
        if((!secure && !"http".equalsIgnoreCase(uri.getScheme())) || host==null || uri.getUserInfo()!=null
                || uri.getRawQuery()!=null || uri.getRawFragment()!=null || port<1 || port>65535
                || path==null || !path.matches("(?:/[A-Za-z0-9_-]+)*/?"))
            throw new IllegalArgumentException("Wpisz adres HTTPS prezentacji albo lokalny adres IPv4.");
        if(!secure) {
            if(!(path.isEmpty() || path.equals("/")))throw new IllegalArgumentException("Lokalny HTTP wymaga adresu bez ścieżki.");
            String[] octets=host.split("\\.",-1);
            if(octets.length!=4)throw new IllegalArgumentException("Dla lokalnego HTTP wpisz adres IPv4 laptopa.");
            for(String octet:octets)if(!octet.matches("[0-9]{1,3}") || Integer.parseInt(octet)>255)
                throw new IllegalArgumentException("Nieprawidłowy adres IPv4.");
            if(!username.isEmpty() || !password.isEmpty())throw new IllegalArgumentException("Login można wysłać wyłącznie przez HTTPS.");
        }
        while(path.endsWith("/"))path=path.substring(0,path.length()-1);
        if(secure && path.endsWith("/presenter"))path=path.substring(0,path.length()-10);
        address=(secure?"https://":"http://")+host+((secure && port==443)?"":":"+port)+path;
        if(username.contains(":") || username.contains("\n") || username.contains("\r"))throw new IllegalArgumentException("Nieprawidłowy login.");
        authorization=secure && !username.isEmpty()?"Basic "+Base64.getEncoder().encodeToString((username+":"+password).getBytes(StandardCharsets.UTF_8)):null;
    }
    JSONObject request(String command, String controller, boolean resolve) throws Exception {
        HttpURLConnection c=(HttpURLConnection)new URL(address+
                (command==null?"/state":resolve?"/resolve":"/command")).openConnection();
        c.setConnectTimeout(6000); c.setReadTimeout(8000); c.setInstanceFollowRedirects(false);
        c.setRequestProperty("X-Controller",controller);
        if(authorization!=null)c.setRequestProperty("Authorization",authorization);
        try {
            if(command!=null) {
                c.setRequestMethod("POST");c.setDoOutput(true);
                byte[] bytes=command.getBytes(StandardCharsets.UTF_8);
                c.setFixedLengthStreamingMode(bytes.length);c.setRequestProperty("Content-Type","application/json");
                try(OutputStream out=c.getOutputStream()){out.write(bytes);}
            }
            int status=c.getResponseCode();
            if(status==401)throw new IOException("HTTP 401: otwórz Połączenie i wpisz login oraz hasło portalu.");
            if(status!=200)throw new IOException("Serwer odpowiedział HTTP "+status);
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
