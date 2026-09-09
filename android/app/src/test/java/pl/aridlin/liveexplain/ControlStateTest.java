package pl.aridlin.liveexplain;
import org.json.JSONObject;
import org.junit.Test;
import static org.junit.Assert.*;
public class ControlStateTest {
    private JSONObject state(String phase) throws Exception {return new JSONObject().put("playback_phase",phase);}
    @Test public void holdsStartAnimationButPausedMotionResumes() throws Exception {
        ControlState hold=ControlState.from(state("hold"));assertTrue(hold.enabled);assertEquals("advance",hold.kind);
        ControlState pause=ControlState.from(state("paused"));assertTrue(pause.enabled);assertEquals("play",pause.kind);
    }
    @Test public void runningWaitsAndEnablesFreeze() throws Exception {
        ControlState c=ControlState.from(state("running").put("playing",true));assertFalse(c.enabled);assertTrue(c.moving);
    }
    @Test public void pausedTransitionCanResumeFromPrimaryButton() throws Exception {
        ControlState c=ControlState.from(state("hold").put("transitioning",true).put("transition_paused",true));assertTrue(c.enabled);assertEquals("play",c.kind);assertFalse(c.moving);
    }
    @Test public void finalDetourReturnsInsteadOfAdvancing() throws Exception {
        ControlState c=ControlState.from(state("beat_end").put("next_kind","return"));assertEquals("return",c.kind);assertEquals("return",c.icon);
    }
    @Test public void hiddenScreenCanBeRecoveredWithoutOpeningTray() throws Exception {
        ControlState c=ControlState.from(state("hold").put("blank",true));assertTrue(c.enabled);assertEquals("blank",c.kind);assertEquals("off",c.value);
    }
    @Test public void completedTalkDoesNotOfferDeadAdvance() throws Exception {
        assertFalse(ControlState.from(state("finished")).enabled);
    }
}
