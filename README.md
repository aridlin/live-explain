# Live Explain

A planned Python-based instrument for live technical explanation: three authored canonical narratives, controllable animated diagrams, meaningful explanatory detours, synchronized private scripts, and an eventual native Android controller.

**Status: planning only.** There is no application, install command, renderer benchmark, or executable test suite yet. Implementation awaits approval of the design. The public repository currently records the design and the acceptance tests to implement; it does not claim those tests pass.

- [Planning document: architecture, proposed authoring API, and milestones](PLAN.md)
- [Test and acceptance specification](TEST_PLAN.md)

The first presentation is a roughly 20-minute Polish explanation of Spectre and Meltdown. The engine is intended for extensive reuse beyond that subject.

Initial target: a Linux/Hyprland laptop with an ordinary fullscreen audience window on an HDMI projector and a separate private presenter window; Android only for the mobile milestone. Recommended foundation: PySide6 with Graphics View, subject to a representative feasibility prototype. Qt Quick is the fallback if measured rendering requirements justify it.

Public content deliberately excludes local diagnostics, device identifiers, personal context, pairing credentials, and session recordings. Future executable tests belong with the implementation and must cover navigation, models, animation, geometry, protocol, and visual regression. See the test specification for acceptance gates.
