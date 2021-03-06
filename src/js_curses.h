// -*- C++ -*-
// Copyright 2012, Evan Klitzke <evan@eklitzke.org>
//
// Implementation of a line of code

#ifndef SRC_JS_CURSES_H_
#define SRC_JS_CURSES_H_

#include <v8.h>

using v8::Handle;
using v8::Value;

namespace e {
namespace js_curses {
bool Build(v8::Handle<v8::Object>);
}
}

#endif  // SRC_JS_CURSES_H_
