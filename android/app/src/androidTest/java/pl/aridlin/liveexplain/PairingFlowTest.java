package pl.aridlin.liveexplain;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.Instrumentation;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.widget.EditText;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import androidx.test.platform.app.InstrumentationRegistry;
import org.junit.Test;
import java.lang.reflect.Field;
import static org.junit.Assert.*;

/** Exercise the real scan button and Android result callback with a canned scanner result.
 * The scanner decoder/camera itself is covered separately by the standalone smoke test. */
public class PairingFlowTest {
    private final Instrumentation inst = InstrumentationRegistry.getInstrumentation();
    private MainActivity activity;
    private Object field(String name) throws Exception {
        Field f = MainActivity.class.getDeclaredField(name); f.setAccessible(true); return f.get(activity);
    }
    private Button button(View view, String text) {
        if(view instanceof Button && text.equals(((Button)view).getText().toString())) return (Button)view;
        if(view instanceof ViewGroup) for(int i=0;i<((ViewGroup)view).getChildCount();i++) {
            Button found=button(((ViewGroup)view).getChildAt(i),text); if(found!=null)return found;
        }
        return null;
    }
    private AlertDialog dialog() throws Exception { return (AlertDialog)field("pairingDialog"); }
    private EditText input() throws Exception { return (EditText)field("pairingInput"); }
    private void main(Checked task) {
        inst.runOnMainSync(()->{try {task.run();}catch(Exception e){throw new RuntimeException(e);}});
    }
    private interface Checked { void run() throws Exception; }
    private void awaitResult(String expected) throws Exception {
        for(int i=0;i<100;i++) {
            boolean[] ready={false}; main(()->ready[0]=dialog().isShowing() && expected.equals(input().getText().toString()));
            if(ready[0])return; Thread.sleep(100);
        }
        fail("Scanner result was not restored into the pairing dialog");
    }
    @Test public void scanThenConnectUsesScannedDataAndCancelPreservesDraft() throws Exception {
        Context context=inst.getTargetContext();
        context.getSharedPreferences("presenter",0).edit().clear().commit();
        activity=(MainActivity)inst.startActivitySync(new Intent(context,MainActivity.class).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));
        String uri="liveexplain://pair?host=127.0.0.1&port=9&pin="+"a".repeat(64)+"&token="+"b".repeat(32);
        try {
            main(()->{
                button(activity.getWindow().getDecorView(),"Połączenie").performClick();
                dialog().getButton(AlertDialog.BUTTON_POSITIVE).performClick();
                assertTrue("Empty Connect must keep the dialog open",dialog().isShowing());
                assertNotNull(input().getError());
            });
            Intent result=new Intent().putExtra("SCAN_RESULT",uri).putExtra("SCAN_RESULT_FORMAT","QR_CODE");
            Instrumentation.ActivityMonitor scan=inst.addMonitor("com.journeyapps.barcodescanner.CaptureActivity",
                    new Instrumentation.ActivityResult(Activity.RESULT_OK,result),true);
            main(()->button(dialog().getWindow().getDecorView(),"Skanuj kod QR").performClick());
            awaitResult(uri); assertEquals(1,scan.getHits()); inst.removeMonitor(scan);
            main(()->{
                assertNull("Scanning waits for Connect",field("connection"));
                assertEquals("",context.getSharedPreferences("presenter",0).getString("pairing",""));
                Bundle saved=new Bundle(); activity.onSaveInstanceState(saved);
                assertEquals(uri,saved.getString("pairingDraft"));
                assertTrue(saved.getBoolean("pairingDialogOpen"));
            });
            Instrumentation.ActivityMonitor cancel=inst.addMonitor("com.journeyapps.barcodescanner.CaptureActivity",
                    new Instrumentation.ActivityResult(Activity.RESULT_CANCELED,null),true);
            main(()->button(dialog().getWindow().getDecorView(),"Skanuj kod QR").performClick());
            awaitResult(uri); assertEquals(1,cancel.getHits()); inst.removeMonitor(cancel);
            main(()->{
                dialog().getButton(AlertDialog.BUTTON_POSITIVE).performClick();
                assertFalse(dialog().isShowing());
                Connection connection=(Connection)field("connection");
                assertNotNull(connection); assertEquals("127.0.0.1",connection.host);
                assertEquals(uri,context.getSharedPreferences("presenter",0).getString("pairing",""));
            });
        } finally {main(()->activity.finish());}
    }
}
