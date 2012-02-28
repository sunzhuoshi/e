// -*- C++ -*-
// Copyright 2012, Evan Klitzke <evan@eklitzke.org>

#ifndef SRC_JS_H_
#define SRC_JS_H_

#include <v8.h>
#include <map>
#include <string>
#include <vector>

using v8::Arguments;
using v8::Context;
using v8::External;
using v8::FunctionTemplate;
using v8::Handle;
using v8::InvocationCallback;
using v8::Local;
using v8::Object;
using v8::Persistent;
using v8::Value;

namespace e {
namespace js {

typedef Handle<Value>(*JSCallback)(const Arguments&);

class EventListener {
 public:
  bool Add(const std::string&, Handle<Object>, bool);
  bool Remove(const std::string&, Handle<Object>, bool);
  void Dispatch(const std::string&, Handle<Object>,
                const std::vector<Handle<Value> >&);
 private:
  std::map<std::string, std::vector<Handle<Object> > > capture_;
  std::map<std::string, std::vector<Handle<Object> > > bubble_;

  bool CallHandler(Handle<Value> h, Handle<Object>, size_t, Handle<Value>[]);
  std::vector<Handle<Object> >& CallbackMap(const std::string &, bool);
};

// Reads a file into a v8 string.
Handle<v8::String> ReadFile(const std::string& name);
Handle<Value> LogCallback(const Arguments& args);
std::string ValueToString(Local<Value>);

std::map<std::string, JSCallback> GetCallbacks();  // all of the callbacks
}
}

#endif  // SRC_JS_H_
