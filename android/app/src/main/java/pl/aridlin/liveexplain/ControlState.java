package pl.aridlin.liveexplain;

import org.json.JSONObject;

/** UI projection only: the desktop owns playback, navigation and command validation. */
final class ControlState {
    final String title, hint, label, kind, value, icon;
    final boolean enabled, moving, transition;
    private ControlState(String title,String hint,String label,String kind,String value,String icon,boolean enabled,boolean moving,boolean transition) {
        this.title=title;this.hint=hint;this.label=label;this.kind=kind;this.value=value;this.icon=icon;
        this.enabled=enabled;this.moving=moving;this.transition=transition;
    }
    static ControlState from(JSONObject s) {
        boolean transition=s.optBoolean("transitioning");
        boolean moving=transition ? !s.optBoolean("transition_paused") : s.optBoolean("playing");
        if(s.optBoolean("blank")) return new ControlState("Publiczny ekran zasłonięty","Pokaż ekran, aby wrócić do prezentacji. Animacja pozostanie wstrzymana.","Pokaż ekran","blank","off","screen",true,false,transition);
        if(transition) return new ControlState(moving?"Trwa zmiana sceny":"Zmiana sceny wstrzymana",moving?"Poczekaj na ułożenie sceny. Możesz ją zatrzymać.":"Dotknij Wznów przejście, gdy chcesz dokończyć zmianę sceny.",moving?"Zmiana sceny…":"Wznów przejście","play",null,"play",!moving,moving,true);
        if(moving) return new ControlState("Animacja trwa","Zatrzyma się sama przy następnym punkcie. Mów lub dotknij Zatrzymaj.","Animacja trwa…","play",null,"play",false,true,false);
        String phase=s.optString("playback_phase",s.optDouble("position")>=s.optDouble("duration",1)?"beat_end":"hold");
        if(phase.equals("paused")) return new ControlState("Animacja wstrzymana","Masz czas na wyjaśnienie. Dotknij Kontynuuj ruch, aby wznowić od tego miejsca.","Kontynuuj ruch","play",null,"play",true,false,false);
        if(phase.equals("finished")) return new ControlState("Koniec tej opowieści","Czas na pytania. W panelu możesz powtórzyć fragment lub cofnąć nawigację.","Opowieść zakończona","advance",null,"check",false,false,false);
        if(phase.equals("beat_end")) {
            boolean returning=s.optString("next_kind").equals("return");
            return new ControlState(returning?"Odpowiedź zakończona":"Ten punkt jest zakończony",returning?"Dotknij Wróć do wyjaśnienia. Odtworzymy przerwany widok, wstrzymany.":"Dokończ myśl. Następny punkt zmieni scenę dopiero po Twoim dotknięciu.",returning?"Wróć do wyjaśnienia":"Następny punkt",returning?"return":"advance",null,returning?"return":"next",true,false,false);
        }
        return new ControlState("Teraz mów · obraz czeka","Wyjaśnij obecny obraz. Kiedy skończysz, uruchom kolejny fragment animacji.","Uruchom animację","advance",null,"play",true,false,false);
    }
}
