// Copyright 2012, Evan Klitzke <evan@eklitzke.org>

#include <stdio.h>
#include <unistd.h>

#include <boost/lexical_cast.hpp>
#include <boost/program_options.hpp>
#include <glog/logging.h>

#include "./curses_window.h"
#include "./list_environment.h"
#include "./state.h"

namespace po = boost::program_options;

int main(int argc, char **argv) {
  google::InitGoogleLogging(argv[0]);

  po::options_description desc("Allowed options");
  desc.add_options()
      ("help,h", "produce help message")
      ("skip-core", "skip loading any bundled \"core\" JS files")
      ("script,s", po::value<std::vector<std::string> >(),
       "script file(s) to load")
      ("list-environment", "list the default JS environment")
      ("really-do-nothing", "allow running without any JS scripts");

  po::variables_map vm;
  po::store(po::parse_command_line(argc, argv, desc), vm);
  po::notify(vm);

  if (vm.count("help")) {
    printf("%s\n", boost::lexical_cast<std::string>(desc).c_str());
    return 1;
  }

  // Generally a user should only be allowed to --skip-core if they specify
  // other scripts on the command line; if they try to skip this, make sure that
  // --really-do-nothing was specified.
  if (vm.count("skip-core") &&
      !vm.count("script") &&
      !vm.count("really-do-nothing")) {
    printf(
        "Running with --skip-core and no --script arguments is probably a bad "
        "idea.\nIf you want to do this anyway, invoke with "
        "--really-do-nothing\n");
    return 1;
  }

  if (vm.count("list-environment")) {
    e::State state;
    state.LoadScript(false, e::ListEnvironment);
  } else {
    bool load_core = !vm.count("skip-core");
    std::vector<std::string> inputs;
    if (vm.count("script")) {
      inputs = vm["script"].as<std::vector<std::string> >();
    }
    e::CursesWindow window(load_core, inputs);
    window.Loop();
  }

  return 0;
}
