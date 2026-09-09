package pl.aridlin.liveexplain;

import android.app.*;
import android.os.*;
import android.content.*;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.view.*;
import android.view.animation.DecelerateInterpolator;
import android.widget.*;
import org.json.*;
import java.util.*;
import java.util.concurrent.*;

/** Native Android reader; the expandable tray never replaces the speaking script. */
public class MainActivity extends Activity {
    private final int bg = Color.rgb(20,39,49), card = Color.rgb(32,55,66), ink = Color.rgb(239,245,238), mint = Color.rgb(155,218,196);
    private final Handler ui = new Handler(Looper.getMainLooper());
    private final ExecutorService network = Executors.newSingleThreadExecutor();
    private SharedPreferences prefs;
    private Connection connection;
    private AlertDialog connectionDialog;
    private EditText addressInput;
    private String addressDraft = "";
    private LinearLayout serverList;
    private String connectionIssue = "";
    private Discovery discovery;
    private final Map<String,android.net.nsd.NsdServiceInfo> nearby=new LinkedHashMap<>();
    private CommandLedger ledger;
    private JSONObject state;
    private boolean busy, online, resumed, expanded, compact;
    private int generation, fontSize = 22;
    private long lastSync;
    private String controller, shownKey = "", trayKey = "", receipt = "", serverAddress = "", freshPending = "";
    private LinearLayout root, tray;
    private ScrollView reader, trayScroll;
    private TextView status, location, script, objective, returnTo, progress, actionTitle, actionHint;
    private Button next, pause, trayToggle;
    private final List<Button> commands = new ArrayList<>();
    private final Map<String,Integer> scrollPositions = new HashMap<>();
    private final Runnable poll = new Runnable() {
        public void run() {
            if (!resumed) return;
            if (connection != null && !busy) exchange(false);
            if (SystemClock.elapsedRealtime() - lastSync > 2500) { online = false; updateEnabled(); }
            ui.postDelayed(this, 500);
        }
    };

    public void onCreate(Bundle saved) {
        super.onCreate(saved);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON | WindowManager.LayoutParams.FLAG_SECURE);
        prefs = getSharedPreferences("presenter", MODE_PRIVATE);
        controller = prefs.getString("controller", UUID.randomUUID().toString());
        prefs.edit().putString("controller", controller).apply();
        fontSize = prefs.getInt("font",22);
        compact = prefs.getBoolean("compact",false);
        try { ledger = new CommandLedger(prefs.getString("pending", "")); }
        catch (Exception e) { try { ledger = new CommandLedger(""); } catch (Exception ignored) {} }
        serverAddress = prefs.getString("server", "");
        prefs.edit().remove("pairing").apply();
        try { if (!serverAddress.isEmpty()) connection = new Connection(serverAddress); } catch (Exception ignored) {}
        try { state = new JSONObject(prefs.getString("state", "")); } catch (Exception ignored) {}
        discovery=new Discovery(this,(info,epoch)->{
            if(epoch==null)nearby.remove(info.getServiceName());
            else {
                nearby.put(info.getServiceName(),info);
                if(connection!=null && !online && state!=null && epoch.equals(state.optString("epoch"))) {
                    String moved="http://"+info.getHost().getHostAddress()+":"+info.getPort();
                    if(!moved.equals(serverAddress))connect(moved);
                }
            }
            refreshServers();
        });
        build();
        if (state != null) render();
        if (saved == null && connection == null) showConnectionDialog();
        if (saved != null) {
            addressDraft = saved.getString("addressDraft", "");
            if (saved.getBoolean("connectionDialogOpen", false)) showConnectionDialog();
        }
    }
    protected void onSaveInstanceState(Bundle out) {
        boolean open = connectionDialog != null && connectionDialog.isShowing();
        if (open) addressDraft = addressInput.getText().toString();
        out.putString("addressDraft", addressDraft);
        out.putBoolean("connectionDialogOpen", open);
        super.onSaveInstanceState(out);
    }
    protected void onResume() { super.onResume(); resumed = true; discovery.start(); ui.removeCallbacks(poll); ui.post(poll); }
    protected void onPause() { resumed = false; discovery.stop(); online = false; freshPending = ""; ui.removeCallbacks(poll); super.onPause(); }
    protected void onDestroy() { if(connectionDialog!=null)connectionDialog.dismiss(); ui.removeCallbacksAndMessages(null); network.shutdownNow(); super.onDestroy(); }
    public void onBackPressed() {
        if (expanded) toggleTray();
        else new AlertDialog.Builder(this).setMessage("Opuścić pulpit? Prezentacja pozostanie na laptopie.")
                .setNegativeButton("Zostań",null).setPositiveButton("Opuść",(d,w)->finish()).show();
    }
    private int dp(float value) { return (int)(getResources().getDisplayMetrics().density * value + .5f); }
    private LinearLayout column() { LinearLayout v = new LinearLayout(this); v.setOrientation(LinearLayout.VERTICAL); return v; }
    private TextView text(String value, int size, int color) {
        TextView v = new TextView(this); v.setText(value); v.setTextSize(size); v.setTextColor(color);
        v.setPadding(dp(4),dp(6),dp(4),dp(6)); v.setLineSpacing(dp(4),1); return v;
    }
    private GradientDrawable surface(int color) { GradientDrawable d = new GradientDrawable(); d.setColor(color); d.setCornerRadius(dp(16)); return d; }
    private Button button(String label, Runnable action) {
        Button b = new Button(this); b.setText(label); b.setAllCaps(false); b.setTextSize(16);
        b.setTextColor(ink); b.setBackground(surface(card)); b.setMinHeight(dp(52));
        b.setPadding(dp(12), dp(8), dp(12), dp(8));
        b.setOnClickListener(v->{ v.performHapticFeedback(HapticFeedbackConstants.VIRTUAL_KEY); action.run(); });
        return b;
    }
    private void icon(Button button, String name) {
        button.setCompoundDrawablesRelative(new ControlIcon(name,ink,dp(22)),null,null,null);
        button.setCompoundDrawablePadding(dp(8));
    }
    private void add(LinearLayout box, View view) {
        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(-1,-2); p.setMargins(0,dp(4),0,dp(4)); box.addView(view,p);
    }
    private void build() {
        root = column(); root.setBackgroundColor(bg); root.setPadding(dp(18),dp(12),dp(18),dp(12)); setContentView(root);
        LinearLayout header = new LinearLayout(this); header.setGravity(Gravity.CENTER_VERTICAL);
        TextView brand = text("LIVE EXPLAIN",12,mint); brand.setLetterSpacing(.15f); brand.setTypeface(null,Typeface.BOLD);
        header.addView(brand,new LinearLayout.LayoutParams(0,-2,1));
        Button connectButton=button("Połączenie",this::showConnectionDialog);icon(connectButton,"wifi");header.addView(connectButton); root.addView(header);
        status = text("Wybierz prezentację w tej samej sieci Wi-Fi",12,mint); root.addView(status);
        location = text("Twój skrypt. Twój rytm.",21,ink); location.setTypeface(null,Typeface.BOLD); root.addView(location);
        progress = text("",12,mint); root.addView(progress);
        reader = new ScrollView(this); reader.setFillViewport(true);
        LinearLayout body = column(); body.setPadding(dp(12),dp(8),dp(12),dp(20)); body.setBackground(surface(card));
        objective = text("Połącz telefon i laptop z tą samą siecią Wi-Fi. Wybierz prezentację w menu Połączenie.",14,mint);
        script = text("Wybierz znalezioną prezentację lub wpisz adres laptopa. Skrypt pozostaje dostępny również podczas chwilowej utraty połączenia.",fontSize,ink);
        returnTo = text("",15,mint);
        body.addView(objective); body.addView(script); body.addView(returnTo); reader.addView(body);
        root.addView(reader,new LinearLayout.LayoutParams(-1,0,1));
        actionTitle=text("Najpierw połącz z laptopem",15,mint);actionTitle.setTypeface(null,Typeface.BOLD);root.addView(actionTitle);
        actionHint=text("Tutaj zobaczysz, kiedy mówić, a kiedy uruchomić animację.",13,ink);root.addView(actionHint);
        LinearLayout primary = new LinearLayout(this);
        pause = button("Zatrzymaj",()->send("pause",null)); icon(pause,"pause");
        next = button("Połącz z laptopem",()->{if(state!=null){ControlState c=ControlState.from(state);if(c.enabled)send(c.kind,c.value);}});
        next.setBackground(surface(Color.rgb(39,111,94)));
        LinearLayout.LayoutParams half = new LinearLayout.LayoutParams(0,-2,1); half.setMargins(dp(3),dp(8),dp(3),dp(4));
        primary.addView(pause,half); LinearLayout.LayoutParams mainAction=new LinearLayout.LayoutParams(half);mainAction.weight=1.65f;primary.addView(next,mainAction); root.addView(primary);
        trayToggle = button("Ścieżki i narzędzia",this::toggleTray); icon(trayToggle,"up");root.addView(trayToggle);
        trayScroll = new ScrollView(this); tray = column(); trayScroll.addView(tray); trayScroll.setVisibility(View.GONE);
        root.addView(trayScroll,new LinearLayout.LayoutParams(-1,Math.min(dp(290),(int)(getResources().getDisplayMetrics().heightPixels*.36f))));
        updateEnabled();
    }
    private void toggleTray() {
        expanded = !expanded; trayToggle.setText(expanded ? "Schowaj panel" : "Ścieżki i narzędzia");icon(trayToggle,expanded?"down":"up");
        trayScroll.setVisibility(expanded ? View.VISIBLE : View.GONE);
        if (expanded) { trayScroll.setAlpha(0); trayScroll.setTranslationY(dp(14));
            trayScroll.animate().alpha(1).translationY(0).setDuration(220).setInterpolator(new DecelerateInterpolator()).start(); }
    }
    private Button commandButton(String title, String kind, String value, boolean confirm) {
        Button b = button(title,()->{
            if (confirm) new AlertDialog.Builder(this).setTitle(title).setMessage("Zmienić bieżącą kontynuację?")
                    .setNegativeButton("Zostań",null).setPositiveButton("Przejdź",(d,w)->send(kind,value)).show();
            else send(kind,value);
        }); b.setTag(kind+":"+(value==null?"":value));
        icon(b,kind.equals("detour")?"branch":kind.equals("depth")?"text":kind.equals("finish")?"skip":kind.equals("blank")||kind.equals("output")?"screen":kind);
        commands.add(b); add(tray,b); return b;
    }
    private void render() {
        if (state == null) return;
        String key = state.optString("epoch")+":"+state.optString("beat");
        JSONObject notes = state.optJSONObject("script"); if (notes == null) notes = new JSONObject();
        location.setText(state.optString("title"));

        String route = state.optString("canonical");
        String routeLabel = route.equals("simple") ? "Super prosta" : route.equals("deep") ? "Szczegółowa" : "Normalna";
        int seconds = (int)state.optDouble("elapsed");
        progress.setText(routeLabel+"  •  "+String.format(Locale.ROOT,"%02d:%02d",seconds/60,seconds%60)
               +"  •  Widok "+(state.optInt("stage_index")+1)+" / "+state.optInt("stage_count",1));
        objective.setText("TERAZ  ·  "+state.optString("stage_cue",notes.optString("objective")));
        String words = compact ? notes.optString("cue") : notes.optString("wording");
        words += "\n\nPO KOLEJNYM RUCHU / PRZEJŚCIU\n"+state.optString("upcoming_cue",notes.optString("next_sentence"));
        if (!compact) words += "\n\nGRANICE WYJAŚNIENIA\n"+notes.optString("boundary")+"\n\nKRÓTKI POWRÓT\n"+notes.optString("recap");
        if (!script.getText().toString().equals(words)) script.setText(words);
        if (!shownKey.equals(key)) {
            scrollPositions.put(shownKey,reader.getScrollY()); shownKey = key;
            int y = scrollPositions.getOrDefault(key,0); reader.post(()->reader.scrollTo(0,y));
        }
        String origin = state.isNull("return_to") ? "Główna narracja" : "Powrót: "+state.optString("return_title",state.optString("return_to"));
        returnTo.setText(origin+"\n"+state.optString("return_sentence")+
                (state.isNull("bridge_target") ? "" : "\nPo moście: "+state.optString("bridge_target")));
        String newTray = key+route+state.optString("return_to")+state.optString("routes")+state.optString("branches")+state.optString("outputs")+state.optBoolean("blank");
        if (!trayKey.equals(newTray)) {
            trayKey = newTray; tray.removeAllViews(); commands.clear();
            add(tray,text("GŁÓWNA OPOWIEŚĆ · WYBIERZ SZCZEGÓŁOWOŚĆ",12,mint));
            LinearLayout routeRow=new LinearLayout(this); add(tray,routeRow);
            JSONArray routes = state.optJSONArray("routes");
            if (routes != null) for (int i=0;i<routes.length();i++) {
                JSONObject r=routes.optJSONObject(i); if(r==null)continue;
                String gaps=r.optString("missing","[]");
                Button routeButton=commandButton(r.optString("title")+
                        (gaps.equals("[]") ? "" : "\nprzez most"),"depth",r.optString("id"),true);
                tray.removeView(routeButton);routeButton.setTextSize(13);
                routeButton.setCompoundDrawablesRelative(null,null,null,null);
                if(r.optString("id").equals(route)) {routeButton.setBackground(surface(Color.rgb(39,111,94)));routeButton.setText("Wybrana\n"+r.optString("title"));}
                LinearLayout.LayoutParams rp=new LinearLayout.LayoutParams(0,dp(72),1);rp.setMargins(dp(2),0,dp(2),0);routeRow.addView(routeButton,rp);
            }
            add(tray,text("MOŻLIWE WYJAŚNIENIA",12,mint));
            JSONArray branches=state.optJSONArray("branches");
            if (branches==null || branches.length()==0) add(tray,text("Brak dodatkowych gałęzi w tym miejscu.",14,ink));
            else for(int i=0;i<branches.length();i++){JSONObject b=branches.optJSONObject(i);
                commandButton(b.optString("title"),"detour",b.optString("id"),false);}
            commandButton("Wróć do przerwanego wyjaśnienia","return",null,false);
            add(tray,text("ODTWARZANIE I RATUNEK",12,mint));
            commandButton("Pomiń trwający ruch","finish",null,false);
            commandButton("Powtórz bieżący krok","replay",null,false);
            commandButton("Cofnij nawigację","undo",null,false);
            commandButton(state.optBoolean("blank") ? "Pokaż publiczny ekran" : "Zasłoń publiczny ekran","blank",state.optBoolean("blank") ? "off" : "on",false);
            add(tray,text("CZYTANIE",12,mint));
            add(tray,button(compact ? "Pełne brzmienie" : "Krótkie wskazówki",()->{compact=!compact; prefs.edit().putBoolean("compact",compact).apply();trayKey="";render();}));
            add(tray,button("Większy tekst",()->resizeText(2))); add(tray,button("Mniejszy tekst",()->resizeText(-2)));
            add(tray,text("ODZYSKAJ WYJŚCIE PO ZMIANIE HDMI",12,mint));
            JSONArray outputs=state.optJSONArray("outputs");
            if(outputs!=null)for(int i=0;i<outputs.length();i++){JSONObject o=outputs.optJSONObject(i);
                commandButton("Pełny ekran: "+o.optString("title"),"output",o.optString("id"),true);}
        }
        updateEnabled();
    }
    private void resizeText(int delta) { fontSize=Math.max(16,Math.min(36,fontSize+delta)); script.setTextSize(fontSize);prefs.edit().putInt("font",fontSize).apply(); }
    private void updateEnabled() {
        if(next==null)return;
        boolean ready=online && ledger.pending().isEmpty() && state!=null;
        ControlState c=state==null?null:ControlState.from(state);
        next.setEnabled(ready && c.enabled);
        pause.setEnabled(ready && c.moving);
        if(c!=null) {
            next.setText(c.label);icon(next,c.icon);
            actionTitle.setText(!online?"Połączenie przerwane":!ledger.pending().isEmpty()?"Czekam na potwierdzenie":c.title);
            actionHint.setText(!online?"Skrypt jest zachowany. Sterowanie wróci po połączeniu z laptopem.":!ledger.pending().isEmpty()?"Nie dotykaj ponownie — sprawdzam wynik poprzedniego polecenia.":c.hint);
        }
        for(Button b:commands) {
            String tag=String.valueOf(b.getTag());String kind=tag.split(":",2)[0];
            boolean allowed=ready;
            if(ready) {
                if(kind.equals("return"))allowed=!state.isNull("return_to") && !c.transition;
                else if(kind.equals("undo"))allowed=state.optBoolean("can_undo");
                else if(kind.equals("finish"))allowed=!state.optBoolean("blank") && (c.transition || c.moving || state.optString("playback_phase").equals("paused"));
                else if(kind.equals("depth"))allowed=!c.transition && !tag.equals("depth:"+state.optString("canonical"));
                else if(kind.equals("detour"))allowed=!c.transition;
                else if(kind.equals("replay"))allowed=!c.transition && !c.moving && state.optDouble("position")>0;
            }
            b.setEnabled(allowed);b.setAlpha(allowed || tag.equals("depth:"+state.optString("canonical"))?1:.4f);
        }
        next.setAlpha(next.isEnabled()?1:.45f); pause.setAlpha(pause.isEnabled()?1:.4f);
        status.setText(connection==null ? "Wybierz prezentację w menu Połączenie" : !ledger.pending().isEmpty() ? "Ustalam wynik polecenia — bez powtórnego przejścia" : online ? "Połączono  ·  "+(receipt.isEmpty()?"laptop steruje sesją":receipt) : (connectionIssue.isEmpty()?"Łączenie z "+serverAddress+"…":connectionIssue+" · próbuję ponownie"));
        status.setTextColor(online?mint:Color.rgb(245,195,125));
    }
    private void send(String kind,String value) {
        if(!online || state==null || !ledger.pending().isEmpty())return;
        try { ledger.begin(state,kind,value); freshPending=ledger.pending(); prefs.edit().putString("pending",ledger.pending()).commit();
            updateEnabled(); exchange(true);
        } catch(Exception e){receipt="Nie udało się wysłać";updateEnabled();}
    }
    private void exchange(boolean firstAttempt) {
        if(busy || connection==null)return;
        busy=true; Connection target=connection; int current=generation;
        String pending=ledger.pending();
        boolean initial=!pending.isEmpty() && pending.equals(freshPending); freshPending="";
        network.execute(()->{
            try {
                JSONObject response=null;
                if(!pending.isEmpty()) response=target.request(pending,controller,!initial);
                JSONObject snapshot=target.request(null,controller,false);
                JSONObject finalResponse=response;
                ui.post(()->{
                    if(current!=generation || isDestroyed())return;
                    busy=false;
                    if(finalResponse!=null && ledger.receive(finalResponse)) {
                        prefs.edit().putString("pending",ledger.pending()).commit();
                        receipt=finalResponse.optString("message",finalResponse.optString("status"));
                    }
                    JSONObject fresh=snapshot.optJSONObject("state");
                    if(fresh==null){online=false;connectionIssue="To nie jest zgodna sesja Live Explain";}else{
                        state=fresh;online=true;connectionIssue="";lastSync=SystemClock.elapsedRealtime();
                        prefs.edit().putString("state",state.toString()).apply();render();
                    }
                    updateEnabled();
                });
            } catch(Exception e){ui.post(()->{if(current==generation && !isDestroyed()){busy=false;online=false;connectionIssue="Laptop nie odpowiada: "+serverAddress+". Sprawdź Wi-Fi i zaporę laptopa.";updateEnabled();}});}
        });
    }
    private void refreshServers() {
        if(serverList==null || connectionDialog==null || !connectionDialog.isShowing())return;
        serverList.removeAllViews();
        if(nearby.isEmpty()) add(serverList,text("Szukam prezentacji w tej sieci… Możesz też wpisać adres laptopa poniżej.",16,ink));
        for(android.net.nsd.NsdServiceInfo info:nearby.values()) {
            String address="http://"+info.getHost().getHostAddress()+":"+info.getPort();
            add(serverList,button(info.getServiceName()+"\n"+address,()->connect(address)));
        }
    }
    private void showConnectionDialog() {
        if(connectionDialog!=null && connectionDialog.isShowing())return;
        LinearLayout box=column();box.setPadding(dp(20),dp(8),dp(20),dp(8));
        add(box,text("Ta sama sieć Wi-Fi lub hotspot telefonu. Wybierz prezentację — bez kodu i parowania.",16,ink));
        serverList=column();add(box,serverList);
        add(box,button("Szukaj ponownie",()->{discovery.stop();discovery.start();refreshServers();}));
        addressInput=new EditText(this);addressInput.setHint("Adres laptopa, np. 192.168.0.39");
        addressInput.setTextColor(ink);addressInput.setSingleLine(true);
        addressInput.setInputType(android.text.InputType.TYPE_CLASS_TEXT|android.text.InputType.TYPE_TEXT_VARIATION_URI);
        addressInput.setText(addressDraft.isEmpty()?serverAddress:addressDraft);add(box,addressInput);
        ScrollView scroll=new ScrollView(this);scroll.addView(box);
        connectionDialog=new AlertDialog.Builder(this).setTitle("Prezentacje w sieci").setView(scroll)
                .setNegativeButton("Zamknij",(d,w)->{addressDraft=addressInput.getText().toString();})
                .setPositiveButton("Połącz z adresem",null).create();
        connectionDialog.show();
        connectionDialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{
            addressDraft=addressInput.getText().toString().trim();connect(addressDraft);
        });
        refreshServers();
    }
    private void connect(String address) {
        final Connection candidate;
        try {candidate=new Connection(address);}
        catch(Exception invalid) {if(addressInput!=null)addressInput.setError("Wpisz adres IPv4 laptopa, np. 192.168.0.39");return;}
        connection=candidate;serverAddress=candidate.address;addressDraft=serverAddress;
        generation++;busy=false;online=false;receipt="";connectionIssue="";freshPending="";
        prefs.edit().putString("server",serverAddress).apply();
        if(connectionDialog!=null)connectionDialog.dismiss();
        updateEnabled();exchange(false);
    }
}
