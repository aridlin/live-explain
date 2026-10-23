# Video research for the web presentation

Research date: 2026-10-23. Public YouTube metadata and English automatic captions were fetched with yt-dlp. The caption text was read to assess the explanation, rather than treating titles or view counts as evidence of content. Captions can contain transcription errors. Videos were not visually reviewed frame by frame, and neither footage nor transcripts are redistributed in this repository.

“Perform well” here means substantial observed reach (roughly 192k–358k views) plus several thousand likes. This is a transparent selection proxy, not a claim about retention, impressions, channel-relative outperformance or educational effectiveness, which were not available.

| Video | Views | Likes | Use in Live Explain |
| --- | ---: | ---: | --- |
| [Spectre & Meltdown — Computerphile](https://www.youtube.com/watch?v=I5mRwzVvFGE) | 357,907 | 10,819 | Concrete array-bound example followed by the dependent cache access and timing evidence. Keep the code focus aligned with the diagram. Reveal the secret only after interpreting the trace. |
| [CPUs Are Out of Order — Computerphile](https://www.youtube.com/watch?v=_qvOlL8nhN4) | 192,041 | 4,948 | Explain idle execution resources and memory latency before the optimization. Use a waiting-versus-executing timeline, then separate a discarded result from surviving hardware state. |
| [How Meltdown and Spectre Make Your Computer Vulnerable — SciShow](https://www.youtube.com/watch?v=2exp-NWHp_E) | 246,483 | 8,954 | Start with an everyday observation, establish why anticipation helps, then describe the failure. Retain the existing Polish pizza introduction and distinguish the analogy from the CPU mechanism. |

The first Computerphile video begins with the disclosure context, then demonstrates bounds and traces through the dependent access. Its early description treats Meltdown as an instance within a broader Spectre grouping; the web presentation does **not** adopt that taxonomy. The second explains arithmetic dependencies, execution units and parallel scheduling, and connects these to speculative work near the end. Out-of-order execution and branch speculation are related but not interchangeable concepts. SciShow uses making an extra coffee as an anticipation analogy; we use that teaching pattern, not their wording or the coffee story.

The 2018 videos contain historical vulnerability/mitigation claims. They are not current device-assessment instructions. The existing authored routes already make the narrower distinction between Spectre v1 and original Meltdown, so those scripts were preserved rather than replaced with video summaries.

## Technical sources

- [Spectre: Exploiting Speculative Execution](https://spectreattack.com/spectre.pdf), especially the conditional-branch example and cache side channel. Grounds the separation of bounds checks, transient dependent accesses, discarded architectural results and observable cache state.
- [Meltdown: Reading Kernel Memory from User Space](https://meltdownattack.com/meltdown.pdf). Grounds the different permission boundary and the historical role of kernel page-table isolation. No inference is made about this laptop's susceptibility.
- [WebKit's explanation](https://webkit.org/blog/8048/what-spectre-and-meltdown-mean-for-webkit/) corroborates the bounds-check / dependent-load / timing chain in the historical browser context.

## Concrete implementation decisions

1. Keep the 16-chapter learning progression and authored Polish simple/normal/deep routes.
2. Make the performance motivation visual before introducing the attack.
3. Use stable colors: orange for speculative work and green for the trace. Explicit labels carry meaning without relying on color alone.
4. Preserve the concealed value through the Spectre scene. In the next scene, display timing evidence and let the speaker ask the audience to infer the value before revealing it.
5. Give architectural rollback and cache state equal-sized panels; the contrast is the central explanation.
6. Give the two exploits separate causes and a visibly shared side channel.
7. Keep caveats and expanded wording in the private presenter view; label simulated timings on the audience view.

All diagrams are newly implemented SVG. All original scripts remain in `talk_text.py`; the frontend receives the current script from the existing runtime rather than maintaining a second translation.
