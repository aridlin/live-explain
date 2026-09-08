package pl.aridlin.liveexplain;

import android.content.Context;
import android.net.nsd.*;
import android.os.Handler;
import android.os.Looper;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** Android DNS-SD locates sessions. Advertisements never grant trust or control. */
final class Discovery {
    interface Listener { void found(NsdServiceInfo info, String pin); }
    private final NsdManager manager;
    private final Listener listener;
    private final Handler ui=new Handler(Looper.getMainLooper());
    private NsdManager.DiscoveryListener active;
    private final Set<String> resolving=new HashSet<>();
    Discovery(Context context, Listener listener) {
        manager=(NsdManager)context.getSystemService(Context.NSD_SERVICE);this.listener=listener;
    }
    void start() {
        if(active!=null)return;
        active=new NsdManager.DiscoveryListener() {
            public void onDiscoveryStarted(String type) {}
            public void onDiscoveryStopped(String type) {}
            public void onStartDiscoveryFailed(String type,int error) {ui.post(()->stop());}
            public void onStopDiscoveryFailed(String type,int error) {}
            public void onServiceLost(NsdServiceInfo info) {ui.post(()->listener.found(info,null));}
            public void onServiceFound(NsdServiceInfo info) {
                ui.post(()->{
                    if(active==null || !resolving.add(info.getServiceName()))return;
                    try { manager.resolveService(info,new NsdManager.ResolveListener() {
                        public void onResolveFailed(NsdServiceInfo item,int error) {ui.post(()->resolving.remove(item.getServiceName()));}
                        public void onServiceResolved(NsdServiceInfo item) {ui.post(()->{
                            resolving.remove(item.getServiceName());
                            byte[] raw=item.getAttributes().get("pin");
                            if(active!=null && raw!=null && item.getHost()!=null) {
                                String pin=new String(raw,StandardCharsets.US_ASCII);
                                if(pin.matches("[0-9a-f]{64}"))listener.found(item,pin);
                            }
                        });}
                    }); } catch(RuntimeException e){resolving.remove(info.getServiceName());}
                });
            }
        };
        try{manager.discoverServices("_liveexplain._tcp.",NsdManager.PROTOCOL_DNS_SD,active);}
        catch(RuntimeException e){active=null;}
    }
    void stop() {
        if(active!=null){try{manager.stopServiceDiscovery(active);}catch(RuntimeException ignored){}active=null;}
        resolving.clear();
    }
}
