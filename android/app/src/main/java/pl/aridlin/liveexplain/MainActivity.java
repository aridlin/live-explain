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
import com.google.zxing.integration.android.IntentIntegrator;
import com.google.zxing.integration.android.IntentResult;
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
    private AlertDialog pairingDialog;
    private EditText pairingInput;
    private String pairingDraft = "";
    private boolean pairingScanned;
    private Discovery discovery;
    private final Map<String,android.net.nsd.NsdServiceInfo> nearby=new LinkedHashMap<>();
    private CommandLedger ledger;
    private JSONObject state;
    private boolean busy, online, resumed, expanded, compact;
    private int generation, fontSize = 22;
    private long lastSync;
    private String controller, shownKey = "", trayKey = "", receipt = "", pairing = "", freshPending = "";
    private LinearLayout root, tray;
    private ScrollView reader, trayScroll;
    private TextView status, location, script, objective, returnTo, progress;
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
        pairing = prefs.getString("pairing", "");
        try { if (!pairing.isEmpty()) connection = new Connection(pairing); } catch (Exception ignored) {}
        try { state = new JSONObject(prefs.getString("state", "")); } catch (Exception ignored) {}
        discovery=new Discovery(this,(info,pin)->{
            if(pin==null){nearby.remove(info.getServiceName());return;}
            nearby.put(info.getServiceName(),info);
            if(connection!=null && !online) {
                String moved=connection.relocated(info.getHost().getHostAddress(),info.getPort(),pin);
                if(moved!=null && !moved.equals(pairing)) {
                    try{connection=new Connection(moved);pairing=moved;prefs.edit().putString("pairing",moved).apply();}
                    catch(Exception ignored){}
                }
            }
        });
        build();
        if (state != null) render();
        if (saved != null) {
            pairingDraft = saved.getString("pairingDraft", "");
            pairingScanned = saved.getBoolean("pairingScanned", false);
            if (saved.getBoolean("pairingDialogOpen", false)) pairDialog();
        }
    }
    protected void onSaveInstanceState(Bundle out) {
        boolean open = pairingDialog != null && pairingDialog.isShowing();
        if (open) pairingDraft = pairingInput.getText().toString();
        out.putString("pairingDraft", pairingDraft);
        out.putBoolean("pairingScanned", pairingScanned);
        out.putBoolean("pairingDialogOpen", open);
        super.onSaveInstanceState(out);
    }
    protected void onResume() { super.onResume(); resumed = true; discovery.start(); ui.removeCallbacks(poll); ui.post(poll); }
    protected void onPause() { resumed = false; discovery.stop(); online = false; freshPending = ""; ui.removeCallbacks(poll); super.onPause(); }
    protected void onDestroy() { if(pairingDialog!=null)pairingDialog.dismiss(); ui.removeCallbacksAndMessages(null); network.shutdownNow(); super.onDestroy(); }
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
    private void add(LinearLayout box, View view) {
        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(-1,-2); p.setMargins(0,dp(4),0,dp(4)); box.addView(view,p);
    }
    private void build() {
        root = column(); root.setBackgroundColor(bg); root.setPadding(dp(18),dp(12),dp(18),dp(12)); setContentView(root);
        LinearLayout header = new LinearLayout(this); header.setGravity(Gravity.CENTER_VERTICAL);
        TextView brand = text("LIVE EXPLAIN",12,mint); brand.setLetterSpacing(.15f); brand.setTypeface(null,Typeface.BOLD);
        header.addView(brand,new LinearLayout.LayoutParams(0,-2,1));
        header.addView(button("Połączenie",this::pairDialog)); root.addView(header);
        status = text("Połącz telefon przed rozpoczęciem",12,mint); root.addView(status);
        location = text("Twój skrypt. Twój rytm.",24,ink); location.setTypeface(null,Typeface.BOLD); root.addView(location);
        progress = text("",12,mint); root.addView(progress);
        reader = new ScrollView(this); reader.setFillViewport(true);
        LinearLayout body = column(); body.setPadding(dp(12),dp(8),dp(12),dp(20)); body.setBackground(surface(card));
        objective = text("Włącz hotspot telefonu, połącz z nim laptop i wybierz na laptopie „Połącz telefon”.",14,mint);
        script = text("Zeskanuj prywatny kod parowania. Skrypt pozostanie czytelny również podczas chwilowej utraty połączenia.",fontSize,ink);
        returnTo = text("",15,mint);
        body.addView(objective); body.addView(script); body.addView(returnTo); reader.addView(body);
        root.addView(reader,new LinearLayout.LayoutParams(-1,0,1));
        LinearLayout primary = new LinearLayout(this);
        pause = button("Pauza",()->send("pause",null)); next = button("Dalej  →",()->send(state==null?"advance":state.optString("next_kind","advance"),null));
        next.setBackground(surface(Color.rgb(39,111,94)));
        LinearLayout.LayoutParams half = new LinearLayout.LayoutParams(0,dp(60),1); half.setMargins(dp(3),dp(8),dp(3),dp(4));
        primary.addView(pause,half); primary.addView(next,new LinearLayout.LayoutParams(half)); root.addView(primary);
        trayToggle = button("⌃  Sterowanie i ścieżki",this::toggleTray); root.addView(trayToggle);
        trayScroll = new ScrollView(this); tray = column(); trayScroll.addView(tray); trayScroll.setVisibility(View.GONE);
        root.addView(trayScroll,new LinearLayout.LayoutParams(-1,Math.min(dp(290),(int)(getResources().getDisplayMetrics().heightPixels*.36f))));
        updateEnabled();
    }
    private void toggleTray() {
        expanded = !expanded; trayToggle.setText(expanded ? "⌄  Schowaj sterowanie" : "⌃  Sterowanie i ścieżki");
        trayScroll.setVisibility(expanded ? View.VISIBLE : View.GONE);
        if (expanded) { trayScroll.setAlpha(0); trayScroll.setTranslationY(dp(14));
            trayScroll.animate().alpha(1).translationY(0).setDuration(220).setInterpolator(new DecelerateInterpolator()).start(); }
    }
    private Button commandButton(String title, String kind, String value, boolean confirm) {
        Button b = button(title,()->{
            if (confirm) new AlertDialog.Builder(this).setTitle(title).setMessage("Zmienić bieżącą kontynuację?")
                    .setNegativeButton("Zostań",null).setPositiveButton("Przejdź",(d,w)->send(kind,value)).show();
            else send(kind,value);
        }); commands.add(b); add(tray,b); return b;
    }
    private void render() {
        if (state == null) return;
        String key = state.optString("epoch")+":"+state.optString("beat");
        JSONObject notes = state.optJSONObject("script"); if (notes == null) notes = new JSONObject();
        location.setText(state.optString("title"));
        next.setText(state.optString("next_label","Dalej")+"  →");
        String route = state.optString("canonical");
        String routeLabel = route.equals("simple") ? "Super prosta" : route.equals("deep") ? "Szczegółowa" : "Normalna";
        int seconds = (int)state.optDouble("elapsed");
        progress.setText(routeLabel+"  •  "+String.format(Locale.ROOT,"%02d:%02d",seconds/60,seconds%60)
                +"  •  "+(state.optBoolean("blank") ? "EKRAN ZASŁONIĘTY" : state.optBoolean("transitioning") ? "ZMIANA SCENY" : state.optBoolean("playing") ? "ODTWARZANIE" : "PAUZA"));
        objective.setText("CEL  ·  "+notes.optString("objective"));
        String words = compact ? notes.optString("cue") : notes.optString("wording");
        words += "\n\nDALEJ\n"+notes.optString("next_sentence");
        if (!compact) words += "\n\nGRANICE WYJAŚNIENIA\n"+notes.optString("boundary")+"\n\nKRÓTKI POWRÓT\n"+notes.optString("recap");
        if (!script.getText().toString().equals(words)) script.setText(words);
        if (!shownKey.equals(key)) {
            scrollPositions.put(shownKey,reader.getScrollY()); shownKey = key;
            int y = scrollPositions.getOrDefault(key,0); reader.post(()->reader.scrollTo(0,y));
        }
        String origin = state.isNull("return_to") ? "Główna narracja" : "Powrót: "+state.optString("return_to");
        returnTo.setText(origin+"\n"+state.optString("return_sentence")+
                (state.isNull("bridge_target") ? "" : "\nPo moście: "+state.optString("bridge_target")));
        String newTray = key+state.optString("routes")+state.optString("branches")+state.optString("outputs")+state.optBoolean("blank");
        if (!trayKey.equals(newTray)) {
            trayKey = newTray; tray.removeAllViews(); commands.clear();
            add(tray,text("TRZY WERSJE TEJ SAMEJ OPOWIEŚCI",12,mint));
            LinearLayout routeRow=new LinearLayout(this); add(tray,routeRow);
            JSONArray routes = state.optJSONArray("routes");
            if (routes != null) for (int i=0;i<routes.length();i++) {
                JSONObject r=routes.optJSONObject(i); if(r==null)continue;
                String gaps=r.optString("missing","[]");
                Button routeButton=commandButton((r.optString("id").equals(route) ? "●  " : "")+r.optString("title")+
                        (gaps.equals("[]") ? "" : "\nprzez most"),"depth",r.optString("id"),true);
                tray.removeView(routeButton);routeButton.setTextSize(13);
                LinearLayout.LayoutParams rp=new LinearLayout.LayoutParams(0,dp(72),1);rp.setMargins(dp(2),0,dp(2),0);routeRow.addView(routeButton,rp);
            }
            add(tray,text("MOŻLIWE WYJAŚNIENIA",12,mint));
            JSONArray branches=state.optJSONArray("branches");
            if (branches==null || branches.length()==0) add(tray,text("Brak dodatkowych gałęzi w tym miejscu.",14,ink));
            else for(int i=0;i<branches.length();i++){JSONObject b=branches.optJSONObject(i);
                commandButton(b.optString("title"),"detour",b.optString("id"),false);}
            commandButton("Wróć do przerwanego wyjaśnienia","return",null,false);
            add(tray,text("ODTWARZANIE I RATUNEK",12,mint));
            commandButton("Wznów animację","play",null,false);
            commandButton("Jeden krok","step",null,false);
            commandButton("Dokończ ruch / przejście","finish",null,false);
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
        next.setEnabled(ready && !state.optBoolean("playing") && !state.optBoolean("transitioning") && !state.optBoolean("blank"));
        pause.setEnabled(ready);
        for(Button b:commands)b.setEnabled(ready);
        next.setAlpha(next.isEnabled()?1:.4f); pause.setAlpha(pause.isEnabled()?1:.4f);
        status.setText(connection==null ? "Zeskanuj kod, aby połączyć" : !ledger.pending().isEmpty() ? "Ustalam wynik polecenia — bez powtórnego przejścia" : online ? "Połączono  ·  "+(receipt.isEmpty()?"laptop steruje sesją":receipt) : "Brak połączenia · skrypt zapisany · próbuję ponownie");
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
                    if(fresh==null){online=false;receipt="Parowanie odrzucone";}else{
                        state=fresh;online=true;lastSync=SystemClock.elapsedRealtime();
                        prefs.edit().putString("state",state.toString()).apply();render();
                    }
                    updateEnabled();
                });
            } catch(Exception e){ui.post(()->{if(current==generation && !isDestroyed()){busy=false;online=false;updateEnabled();}});}
        });
    }
    private void pairDialog() {
        if (pairingDialog != null && pairingDialog.isShowing()) return;
        LinearLayout box=column();box.setPadding(dp(20),dp(8),dp(20),dp(8));
        add(box,text("Telefon udostępnia hotspot. Laptop łączy się z nim przez Wi-Fi. Kod znajdziesz w prywatnym pulpicie laptopa.",16,ink));
        add(box,button("Znajdź prezentację w sieci ("+nearby.size()+")",()->{
            if(nearby.isEmpty())new AlertDialog.Builder(this).setMessage("Szukam sesji w tej sieci Wi-Fi. Jeśli sieć blokuje wykrywanie, zeskanuj kod QR.").setPositiveButton("OK",null).show();
            else new AlertDialog.Builder(this).setTitle("Sesje w tej sieci")
                    .setItems(nearby.keySet().toArray(new String[0]),(d,w)->{
                        android.net.nsd.NsdServiceInfo info=new ArrayList<>(nearby.values()).get(w);
                        String pin=new String(info.getAttributes().get("pin"),java.nio.charset.StandardCharsets.US_ASCII);
                        String moved=connection==null?null:connection.relocated(info.getHost().getHostAddress(),info.getPort(),pin);
                        if(moved!=null)pair(moved);
                        else new AlertDialog.Builder(this).setMessage("Znaleziono "+info.getServiceName()+". Zeskanuj prywatny kod na laptopie, aby zatwierdzić pierwsze połączenie.").setPositiveButton("OK",null).show();
                    }).show();
        }));
        pairingInput=new EditText(this);pairingInput.setHint("Lub wklej link parowania");pairingInput.setTextColor(ink);pairingInput.setSingleLine(true);
        pairingInput.setInputType(android.text.InputType.TYPE_CLASS_TEXT|android.text.InputType.TYPE_TEXT_VARIATION_VISIBLE_PASSWORD);
        pairingInput.setText(pairingDraft);
        add(box,button("Skanuj kod QR",()->{
            pairingDraft=pairingInput.getText().toString();
            pairingDialog.dismiss();
            new IntentIntegrator(this).setDesiredBarcodeFormats(IntentIntegrator.QR_CODE)
                .setPrompt("Prywatny kod z Live Explain").setBeepEnabled(false).setOrientationLocked(false).initiateScan();
        }));
        if (pairingScanned) add(box,text("Kod wczytany. Wybierz Połącz, aby rozpocząć połączenie.",16,mint));
        box.addView(pairingInput);
        pairingDialog=new AlertDialog.Builder(this).setTitle("Połączenie z laptopem").setView(box)
                .setNegativeButton("Zamknij",(d,w)->{pairingDraft=pairingInput.getText().toString();})
                .setPositiveButton("Połącz",null).create();
        pairingDialog.show();
        pairingDialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v->{
            pairingDraft=pairingInput.getText().toString().trim();
            try { new Connection(pairingDraft); }
            catch(Exception invalid) {
                pairingInput.setError("Wczytaj kod QR lub wklej pełny link parowania Live Explain.");
                return;
            }
            pairingDialog.dismiss();
            pair(pairingDraft);
        });
    }
    private void pair(String uri) {
        try {
            Connection candidate=new Connection(uri);
            if(!ledger.pending().isEmpty() && (connection==null || !candidate.pin.equals(connection.pin))) {
                new AlertDialog.Builder(this).setMessage("Wynik polecenia w starej sesji pozostaje nieznany. Połączyć z nową sesją i porzucić stare potwierdzenie?")
                        .setNegativeButton("Zostań",null).setPositiveButton("Nowa sesja",(d,w)->{
                            try { ledger=new CommandLedger(""); prefs.edit().putString("pending","").commit(); pair(uri); }
                            catch(Exception ignored) {}
                        }).show();return;
            }
            connection=candidate;pairing=uri;generation++;busy=false;online=false;receipt="";
            prefs.edit().putString("pairing",uri).apply();exchange(false);
        }catch(Exception e){new AlertDialog.Builder(this).setMessage("Nieprawidłowy kod parowania. Zeskanuj kod z prywatnego pulpitu.").setPositiveButton("OK",null).show();}
    }
    protected void onActivityResult(int request,int result,Intent data) {
        IntentResult scan=IntentIntegrator.parseActivityResult(request,result,data);
        if(scan!=null){
            if(scan.getContents()!=null){pairingDraft=scan.getContents();pairingScanned=true;}
            pairDialog();
        }
        else super.onActivityResult(request,result,data);
    }
}
