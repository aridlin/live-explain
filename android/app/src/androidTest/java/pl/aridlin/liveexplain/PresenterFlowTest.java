package pl.aridlin.liveexplain;

import android.app.Instrumentation;
import android.content.*;
import android.graphics.*;
import android.view.*;
import android.widget.*;
import androidx.test.platform.app.InstrumentationRegistry;
import org.junit.Test;
import static org.junit.Assert.*;
import java.io.*;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;

/** Opt-in loopback rehearsal against the real Python host; no production test hooks. */
public class PresenterFlowTest {
    private final Instrumentation inst=InstrumentationRegistry.getInstrumentation();
    private MainActivity activity;
    private Object field(String name) throws Exception { Field f=MainActivity.class.getDeclaredField(name);f.setAccessible(true);return f.get(activity); }
    private void click(String fragment) {
        inst.runOnMainSync(()->{
            TextView target=find(activity.getWindow().getDecorView(),fragment);
            assertNotNull("Missing control: "+fragment,target);
            assertTrue("Disabled control: "+fragment,target.isEnabled());target.performClick();
        });
    }
    private TextView find(View v,String fragment) {
        if(v instanceof Button && ((Button)v).getText().toString().contains(fragment))return (TextView)v;
        if(v instanceof ViewGroup)for(int i=0;i<((ViewGroup)v).getChildCount();i++){
            TextView result=find(((ViewGroup)v).getChildAt(i),fragment);if(result!=null)return result;
        }
        return null;
    }
    private void waitReady() throws Exception {
        for(int i=0;i<100;i++){
            boolean[] ready={false};inst.runOnMainSync(()->{try {ready[0]=(Boolean)field("online") && ((CommandLedger)field("ledger")).pending().isEmpty();}catch(Exception e){throw new RuntimeException(e);}});
            if(ready[0])return;Thread.sleep(100);
        }
        fail("Controller did not synchronize");
    }
    private void screenshot(String name) {
        inst.runOnMainSync(()->{
            View v=activity.getWindow().getDecorView();Bitmap b=Bitmap.createBitmap(v.getWidth(),v.getHeight(),Bitmap.Config.ARGB_8888);
            v.draw(new Canvas(b));
            try(FileOutputStream out=activity.openFileOutput(name,Context.MODE_PRIVATE)){b.compress(Bitmap.CompressFormat.PNG,100,out);}
            catch(IOException e){throw new RuntimeException(e);}
        });
    }
    @Test public void readerControlsDetourAndExactReturn() throws Exception {
        Context context=inst.getTargetContext();
        String pairing;
        try(InputStream in=context.openFileInput("pairing-test.txt")){pairing=new String(in.readAllBytes(),StandardCharsets.UTF_8).trim();}
        context.getSharedPreferences("presenter",0).edit().clear().putString("pairing",pairing).commit();
        activity=(MainActivity)inst.startActivitySync(new Intent(context,MainActivity.class).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));
        try {
            waitReady();screenshot("reader.png");
            click("Dalej");Thread.sleep(2700);waitReady();
            click("Sterowanie i ścieżki");
            click("Dokończ ruch");Thread.sleep(1000);waitReady();screenshot("tray.png");
            inst.runOnMainSync(()->{
                try { org.json.JSONObject state=(org.json.JSONObject)field("state");
                    org.json.JSONObject branch=state.getJSONArray("branches").getJSONObject(0);
                    TextView button=find(activity.getWindow().getDecorView(),branch.getString("title"));assertNotNull(button);button.performClick();
                } catch(Exception e){throw new RuntimeException(e);}
            });
            Thread.sleep(1000);waitReady();
            inst.runOnMainSync(()->{try{assertEquals("shared.location",((org.json.JSONObject)field("state")).getString("beat"));}catch(Exception e){throw new RuntimeException(e);}});
            click("Wróć do przerwanego");Thread.sleep(1000);waitReady();
            inst.runOnMainSync(()->{try{
                org.json.JSONObject state=(org.json.JSONObject)field("state");
                assertEquals("normal.timing",state.getString("beat"));assertEquals(2,state.getDouble("position"),.001);assertFalse(state.getBoolean("playing"));
            }catch(Exception e){throw new RuntimeException(e);}});
            click("Zasłoń publiczny");Thread.sleep(700);waitReady();
            click("Pokaż publiczny");Thread.sleep(700);waitReady();
        } finally {inst.runOnMainSync(()->activity.finish());}
    }
}
