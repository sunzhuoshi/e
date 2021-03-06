// Copyright 2012, Evan Klitzke <evan@eklitzke.org>

#include "./assert.h"

#ifdef USE_LIBUNWIND
#define UNW_LOCAL_ONLY
#include <libunwind.h>

#include <boost/lexical_cast.hpp>
#include <cxxabi.h>
#endif  // USE_LIBUNWIND

#include <cstdarg>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

#include "./curses_low_level.h"

namespace e {
#if USE_LIBUNWIND
namespace {
void ShowBacktrace(void) {
  unw_context_t uc;
  unw_cursor_t cursor;
  unw_word_t off;
  int unknown_count = 0;
  char funcname[256];

  unw_getcontext(&uc);
  unw_init_local(&cursor, &uc);
  std::vector<std::string> functions;
  while (unw_step(&cursor) > 0) {
    if (unw_get_proc_name(&cursor, funcname, sizeof(funcname), &off) == 0) {
      if (unknown_count) {
        functions.push_back("<" +
                            boost::lexical_cast<std::string>(unknown_count) +
                            " unknown>");
        unknown_count = 0;
      }
      int status;
      char *realname = abi::__cxa_demangle(funcname, 0, 0, &status);
      if (status == 0) {
        std::string s(realname);
        functions.push_back(s);
      }
    } else {
      unknown_count++;
    }
  }
  if (unknown_count) {
    functions.push_back("<" +
                        boost::lexical_cast<std::string>(unknown_count) +
                        " unknown>");
  }

  for (size_t it = functions.size() - 1; it > 0; it--) {
    printf("%s\n", functions[it].c_str());
    fflush(stdout);
  }
}
}
#endif

void PrintAssertThenExit(const char *exprname, const char *filename, int line) {
  EndCurses();
  fprintf(stderr, "Assertion failed <%s:%d>: %s\n(errno is %d)\n\n",
          filename, line, exprname, errno);
#if USE_LIBUNWIND
  ShowBacktrace();
#endif
  exit(EXIT_FAILURE);
}

void Panic(const char *format, ...) {
  EndCurses();

  // print the error message
  va_list ap;
  va_start(ap, format);
  vfprintf(stderr, format, ap);
  va_end(ap);

  // ensure the msg ends with a newline
  size_t len = strlen(format);
  if (!len || format[len - 1] != '\n') {
    fputc('\n', stderr);
  }

  // flush logs and exit
  exit(EXIT_FAILURE);
}
}
