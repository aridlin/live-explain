# Spectre i Meltdown — prowadzenie około 20 minut

`./run --remote` starts the full Normal narrative and the local Wi-Fi address window.
The phone is the primary script reader and controller. Connect and rehearse before leaving
the laptop. `./run --slice` retains the compact engineering specimen.

The audience-facing explanation and full wording are Polish. The three private routes
are independently authored explanations of the same 16 conceptual chapters. Simple
uses shorter wording and simpler memory compositions; Normal introduces the code and
cache observation; Deep adds line granularity, permission/map distinctions and explicit
limits. Depth labels are not projected. None of the routes is an assessment of ability.

## Pacing

The authored core budget is **17:05**, leaving about **2:55** for questions, pauses and
one or two short detours. Normal has approximately 2,300 words before optional questions.
This is a rehearsal budget, not a claim that reading every optional answer fits 20 minutes.
The presenter controls every segment. Animations stop at meaningful holds; there is no
automatic narrative advance. Use compact cues when speaking naturally, full wording
when needed. Do not ask every prepared question: they are opportunities, not a quiz.

| Chapter | Purpose | Core budget |
|---|---|---:|
| Opening | Pentagon pizza: observable activity versus a hypothesis | 1:45 |
| Isolation | Program rule versus hardware access permission | 0:55 |
| Bytes | Address 4, public value 7; read the code together | 1:00 |
| Cache | Useful copies; where cache is, or line granularity in Deep | 0:50 |
| Timing | Same address, changed cache state, illustrative 9 versus 2 | 1:10 |
| Channel | Public value 1 selects a separate probe region | 1:05 |
| Speculation | Predict direction while a condition is unresolved | 0:55 |
| Rollback | Discarded result versus remaining cache trace | 0:50 |
| Bounds | Why index 12 is outside the exposed range 0–7 | 1:00 |
| Training | Prepared history can influence direction prediction | 0:50 |
| Spectre v1 | Victim data, dependent access, rejected work | 1:20 |
| Decode | Compare candidates, infer, then reveal the model's 2 | 1:15 |
| Meltdown | Permission-violating load; no mispredicted bounds check | 1:25 |
| Compare | Shared observation channel, different mechanisms | 0:55 |
| Defenses | Which dependency each kind of protection interrupts | 1:05 |
| Recap | Reconstruct the chain and invite questions | 0:45 |

Protect time for rollback, the dependent access, and the Spectre/Meltdown comparison.
If behind, use compact cues, omit optional questions and avoid new detours. Changing to
Simple at the matching checkpoint changes the explanation; it does not magically recover
elapsed time. Rehearse aloud with the actual phone, then adjust the budget to speaking pace.

## Questions and re-entry

Prepared detours cover cache location, cache lines, bytes/hex, discarded work, the attack
distinction, noisy timing, and whether a particular device is vulnerable. Two nested
detours are permitted. Their availability is authored for the current chapter.

For example, pause Normal timing halfway through the address movement, enter cache
location, and choose Return. The original model, connector geometry, token position,
playback target and code focus are reconstructed exactly, paused; the reader provides
a topic-specific return sentence. Choosing Deep instead uses the original timing
checkpoint, offers the line/cache bridge if its prerequisites have not been covered,
and enters Deep timing at its authored initial state. It does not restore the old
Normal snapshot. Undo recovers the prior navigation, paused.

Exposure records what was presented, not what the audience understood. The speaker
chooses whether a recap or bridge suffices. No automatic comprehension inference occurs.

## Technical teaching audit

This is an educational event model. The addresses are simulated offsets; the byte view
is not host-process memory. There is no exploit, hardware timing module, predictor emulator,
or claim about the particular laptop's vulnerability.

- **Spectre v1:** an attacker-influenced input reaches a victim's bounds-checked sequence;
  trained/mispredicted direction can transiently run the wrong path. The victim can access
  the data, while its function should not disclose that part. A dependent access encodes
  the value into an observable cache effect. The check is not simply removed, and the
  processor does not have to guess the secret. This follows the conditional-branch example
  in the [original Spectre paper](https://spectreattack.com/spectre.pdf), especially its
  overview and variant-one construction. Other Spectre variants are outside this talk.
- **Original Meltdown:** a permission-violating load can transiently influence dependent
  instructions on susceptible implementations before its architectural fault effect.
  The visual contains no bounds-check branch to mistrain. Practical exception handling
  or suppression is acknowledged but omitted, as are exact pipeline stages. This follows
  the [original Meltdown paper](https://meltdownattack.com/meltdown.pdf), its overview and
  attack construction. We do not teach that all CPUs universally check permission last.
- **Rollback:** architectural non-commit does not imply reversal of every microarchitectural
  effect. A cache effect may remain; observation is conditional, noisy and requires suitable
  access. Speculation, out-of-order execution and architectural retirement are distinct.
- **Measurement:** candidate bars use arbitrary simulated units. Four candidates illustrate
  a subset of 256 byte possibilities; each stands for a separated probe region. The noise
  detour deliberately includes a misleading first trial. No threshold or fixed number of
  repetitions guarantees a real attack. The victim byte is masked in numeric, ASCII and
  travelling-token views until the authored reveal. Earlier public examples use different
  values so they do not give away the later secret.
- **Mitigation:** bounds clipping/speculation barriers depend on platform and code; variant-two
  protections are not presented as interchangeable fixes for variant one. See the
  [Linux Spectre mitigation documentation](https://www.kernel.org/doc/html/latest/admin-guide/hw-vuln/spectre.html).
  PTI reduces kernel mappings available with user page tables, retaining small entry/exit
  necessities; it is not cache clearing. See the [Linux PTI documentation](https://www.kernel.org/doc/html/latest/arch/x86/pti.html).

## Before the room

1. Install the corrected Android APK, select the discovered desktop (or enter its IP), and test connection/return.
2. Test the real hotspot or LAN, discovery, disconnect/reconnect, pause, return and blanking.
3. Connect HDMI; verify output recovery from the phone, then check readability from the back.
4. Speak the Normal route aloud with a timer. Take one cache detour and one depth change.
5. Prepare the fallback with `./run --export artifacts/full-talk-fallback --canonical normal`.
   Only `public/` belongs on the audience screen; the sibling private script does not.
6. Leave the host running, phone connected and reader foregrounded before starting.

The exported stills use the live renderer. They preserve the teaching sequence but lose
animation and interactive branching. They are a rehearsable failure fallback, not a second engine.

## Pentagon pizza opening

All three routes begin with a 105-second opening: Pentagon → visible pizza activity →
a hypothesis about overtime → observable computer effects. The presenter pauses for
answers before distinguishing observation from inference. The vectors and travelling
pizza tokens are illustrative; no historical order counts or restaurant-traffic data
are fabricated. The example introduces indirect information, not a CPU mechanism.

Historical anchor: Paul Gray, [“And Bomb The Anchovies,” TIME, 13 August 1990](https://content.time.com/time/subscriber/article/0,33009,970860,00.html),
a contemporary report of delivery workers' claims about orders and Washington activity.
The script attributes the anecdote and explicitly avoids presenting pizza as a reliable
war predictor, identifying meeting contents, or treating restaurant popularity as a
record of deliveries to the Pentagon. Other explanations include exercises and ordinary
overtime. The next chapter establishes computer access boundaries before cache timing.
