// One unchanged example, captured in FT's GUI, TUI and web modes.
// Build against the FT revision recorded in assets/recruitment/sources.json.
#define FT_IMPLEMENTATION
#include "ft.hpp"
#include <chrono>
#include <thread>

int main(int argc, char** argv) {
    ft::Config config;
    config.title = "FT - ten sam przyklad";
    config.width = 1000;
    config.height = 600;
    config.web_host = "127.0.0.1";
    config.web_port = 18765;
    if (!ft::create_window(config, argc, argv)) return 1;
    char topic[128] = "Programowanie";
    bool documentation = true;
    float progress = 0.6f;
    while (ft::pump()) {
        ft::begin();
        ft::text("Plan projektu - przyklad interfejsu FT");
        ft::separator();
        ft::input("Temat", topic, sizeof(topic));
        ft::checkbox("Dokumentacja", &documentation);
        ft::slider_float("Postep", &progress, 0.0f, 1.0f);
        ft::progress_bar(progress);
        if (ft::button("Zapisz")) ft::toast_success("Zapisano przyklad");
        ft::end();
        std::this_thread::sleep_for(std::chrono::milliseconds(30));
    }
    ft::shutdown();
}
