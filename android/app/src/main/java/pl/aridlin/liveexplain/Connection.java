package pl.aridlin.liveexplain;

import org.json.JSONObject;
import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.security.*;
import java.security.cert.*;
import javax.net.ssl.*;

/** Private QR pins one session certificate; no trust-all fallback or cloud service. */
final class Connection {
    final String host, token, pin;
    final int port;
    private final SSLSocketFactory sockets;
    Connection(String pairing) throws Exception {
        URI uri = URI.create(pairing.trim());
        if (!"liveexplain".equals(uri.getScheme()) || !"pair".equals(uri.getHost()))
            throw new IllegalArgumentException("To nie jest kod Live Explain");
        java.util.Map<String,String> fields = new java.util.HashMap<>();
        for (String part : uri.getRawQuery().split("&")) {
            String[] kv = part.split("=", 2);
            fields.put(kv[0], URLDecoder.decode(kv[1], "UTF-8"));
        }
        host = fields.get("host"); token = fields.get("token");
        port = Integer.parseInt(fields.get("port"));
        pin = fields.get("pin");
        if (host == null || !host.matches("[0-9.]+") || port < 1 || port > 65535
                || token == null || token.length() < 32 || pin == null || !pin.matches("[0-9a-f]{64}"))
            throw new IllegalArgumentException("Niepełny kod parowania");
        byte[] expected = new byte[32];
        for (int i = 0; i < 32; i++) expected[i] = (byte)Integer.parseInt(pin.substring(i*2, i*2+2),16);
        TrustManager[] trust = {new X509TrustManager() {
            public X509Certificate[] getAcceptedIssuers() { return new X509Certificate[0]; }
            public void checkClientTrusted(X509Certificate[] chain, String auth) throws CertificateException {
                throw new CertificateException("Client certificates unsupported");
            }
            public void checkServerTrusted(X509Certificate[] chain, String auth) throws CertificateException {
                try {
                    if (chain.length == 0 || !MessageDigest.isEqual(expected,
                            MessageDigest.getInstance("SHA-256").digest(chain[0].getEncoded())))
                        throw new CertificateException("Kod parowania nie pasuje do tego serwera");
                    chain[0].checkValidity();
                } catch (NoSuchAlgorithmException e) { throw new CertificateException(e); }
            }
        }};
        SSLContext context = SSLContext.getInstance("TLS");
        context.init(null, trust, new SecureRandom()); sockets = context.getSocketFactory();
    }
    String relocated(String address, int newPort, String advertisedPin) {
        if (!pin.equals(advertisedPin) || !address.matches("[0-9.]+")) return null;
        return "liveexplain://pair?host="+address+"&port="+newPort+"&pin="+pin+"&token="+token;
    }
    JSONObject request(String command, String controller, boolean resolve) throws Exception {
        HttpsURLConnection c = (HttpsURLConnection)new URL("https", host, port,
                command == null ? "/state" : resolve ? "/resolve" : "/command").openConnection();
        c.setSSLSocketFactory(sockets);
        // Certificate identity is the exact private-QR pin, not a public DNS name.
        c.setHostnameVerifier((name, session) -> name.equals(host));
        c.setConnectTimeout(2500); c.setReadTimeout(5500); c.setInstanceFollowRedirects(false);
        c.setRequestProperty("Authorization", "Bearer " + token);
        c.setRequestProperty("X-Controller", controller);
        try {
            if (command != null) {
                c.setRequestMethod("POST"); c.setDoOutput(true);
                byte[] bytes = command.getBytes(StandardCharsets.UTF_8);
                c.setFixedLengthStreamingMode(bytes.length);
                c.setRequestProperty("Content-Type", "application/json");
                try (OutputStream out = c.getOutputStream()) { out.write(bytes); }
            }
            if (c.getResponseCode() != 200) throw new IOException("Połączenie odrzucone ("+c.getResponseCode()+")");
            try (InputStream in = c.getInputStream(); ByteArrayOutputStream out = new ByteArrayOutputStream()) {
                byte[] buffer = new byte[4096]; int n;
                while ((n = in.read(buffer)) != -1) {
                    if (out.size()+n > 262144) throw new IOException("Odpowiedź zbyt duża");
                    out.write(buffer, 0, n);
                }
                return new JSONObject(out.toString("UTF-8"));
            }
        } finally { c.disconnect(); }
    }
}
