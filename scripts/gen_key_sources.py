#!/usr/bin/env python

import datetime
import optparse
import os.path
import re
import sys

h_template = """
// -*- C++ -*-
// Copyright %(current_year)d, Evan Klitzke <evan@eklitzke.org>
//
// This file is AUTOGENERATED by gen_key_sources.py, do not edit by hand!

#ifndef SRC_KEYCODE_H_
#define SRC_KEYCODE_H_

#include <v8.h>
#include <string>
#include "./embeddable.h"

using v8::Arguments;
using v8::Handle;
using v8::Value;

namespace e {
class KeyCode: public Embeddable {
  public:
    explicit KeyCode(int code, const std::string &short_name);
    explicit KeyCode(int code);
    ~KeyCode();
    const std::string& GetName(void) const;
    bool IsASCII(void) const;
    int GetCode(void) const;
    char GetChar(void) const;
    Persistent<Value> ToScript();
  private:
    int code_;
    std::string short_name_;
};

namespace keycode {
KeyCode* curses_code_to_keycode(int code);
}
}

#endif  // SRC_KEYCODE_H_
"""

cc_template = """
// -*- C++ -*-
// Copyright %(current_year)d, Evan Klitzke <evan@eklitzke.org>
//
// This file is AUTOGENERATED by gen_key_sources.py, do not edit by hand!

#include "./%(h_name)s"

#include <v8.h>

#include <cassert>
#include <string>

#include "./embeddable.h"

using v8::Arguments;
using v8::Boolean;
using v8::External;
using v8::FunctionTemplate;
using v8::Handle;
using v8::HandleScope;
using v8::Integer;
using v8::Object;
using v8::ObjectTemplate;
using v8::String;
using v8::Value;

namespace e {
namespace {
Handle<Value> JSGetChar(const Arguments& args) {
  GET_SELF(KeyCode);

  HandleScope scope;
  char c = self->GetChar();
  Local<String> ch = String::NewSymbol(&c, 1);
  return scope.Close(ch);
}

Handle<Value> JSGetCode(const Arguments& args) {
  GET_SELF(KeyCode);

  HandleScope scope;
  Local<Integer> code = Integer::New(self->GetCode());
  return scope.Close(code);
}

Handle<Value> JSGetName(const Arguments& args) {
  GET_SELF(KeyCode);

  HandleScope scope;
  std::string s = self->GetName();
  Local<String> name = String::NewSymbol(s.c_str(), s.length());
  return scope.Close(name);
}

Handle<Value> JSIsASCII(const Arguments& args) {
  GET_SELF(KeyCode);

  HandleScope scope;
  Handle<Boolean> b = Boolean::New(self->IsASCII());
  return scope.Close(b);
}

Persistent<ObjectTemplate> keycode_template;

// Create a raw template to assign to keycode_template
Handle<ObjectTemplate> MakeKeyCodeTemplate() {
  HandleScope scope;
  Handle<ObjectTemplate> result = ObjectTemplate::New();
  result->SetInternalFieldCount(1);
  result->Set(String::New("getChar"), FunctionTemplate::New(JSGetChar),
    v8::ReadOnly);
  result->Set(String::New("getCode"), FunctionTemplate::New(JSGetCode),
    v8::ReadOnly);
  result->Set(String::New("getName"), FunctionTemplate::New(JSGetName),
    v8::ReadOnly);
  result->Set(String::New("isASCII"), FunctionTemplate::New(JSIsASCII),
    v8::ReadOnly);
  return scope.Close(result);
}
}

KeyCode::KeyCode(int code, const std::string &short_name)
    :code_(code), short_name_(short_name) {
}

KeyCode::KeyCode(int code)
    :code_(code) {
}

KeyCode::~KeyCode() {
}

namespace {
// this callback will be invoked when the V8 keypress object is GC'ed
void CleanupKeycode(Persistent<Value> val, void*) {
  HandleScope scope;
  assert(val->IsObject());
  Local<Object> obj = val->ToObject();
  KeyCode *kc = Unwrap<KeyCode>(obj);
  delete kc;
  val.Dispose();
}
}

Persistent<Value> KeyCode::ToScript() {
  HandleScope scope;

  if (keycode_template.IsEmpty()) {
    Handle<ObjectTemplate> raw_template = MakeKeyCodeTemplate();
    keycode_template = Persistent<ObjectTemplate>::New(raw_template);
  }

  //Local<Object> kc_local = keycode_template->NewInstance();
  Persistent<Object> kc = Persistent<Object>::New(keycode_template->NewInstance());

  kc.MakeWeak(nullptr, CleanupKeycode);

  assert(kc->InternalFieldCount() == 1);
  kc->SetInternalField(0, External::New(this));
  //return scope.Close(kc);
  return kc;
}

const std::string& KeyCode::GetName(void) const {
  return short_name_;
}

bool KeyCode::IsASCII(void) const {
  return code_ <= 0xff;
}

int KeyCode::GetCode(void) const {
  return code_;
}

// XXX: it's unspecified whether this is a signed or unsigned char!
char KeyCode::GetChar(void) const {
  if (code_ > 0xff) {
    return static_cast<char>(code_ & 0xff);
  } else {
    return static_cast<char>(code_);
  }
}

namespace keycode {
  const size_t max_code = %(max_code)d;
  const char * keycode_arr[%(arr_size)d] = {
%(codes)s
  };

  KeyCode* curses_code_to_keycode(int code) {
    size_t offset = static_cast<size_t>(code);
    assert(offset <= max_code);
    const char *name = keycode_arr[offset];

    // The returned pointers are "owned" by V8; the way they'll get deleted
    // later on is by CleanupKeycode, which will be invoked when the containing
    // V8 object is garbage collected.
    if (name == nullptr) {
      return new KeyCode(code);
    } else {
      return new KeyCode(code, name);
    }
  }
}
}
"""

key_regex = re.compile(r'^([_a-z0-9]+)\s+[a-zA-Z0-9]+\s+str\s+[a-zA-Z0-9;@%&*#!]+\s+([_A-Z()0-9]+)\s+([-0-9]+)\s+[-A-Z*]+\s+(.*)$')
octal_regex = re.compile(r'^0[0-9]+$')

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-o', '--output-prefix', default='src/keycode', help='output prefix')
    opts, args = parser.parse_args()
    if not args:
        parser.error('need to specify a capabilities file')
        sys.exit(1)
    try:
        in_file = open(args[0], 'r')
    except IOError:
        parser.error('failed to open capabilities file %r' % (args[1],))
        sys.exit(1)

    values = []
    try:
        for line in in_file:
            if not line.startswith('key_'):
                continue
            m = key_regex.match(line)
            if not m:
                print >> sys.stderr, 'failed to parse line %r' % (line,)
                sys.exit(1)
            name, macro, code, description = m.groups()
            if code == '-':
                code = 0
            elif octal_regex.match(code):
                code = int(code, 8)
            else:
                print >> sys.stderr, 'failed to parse octal code %r' % (code,)
            values.append((name, macro, code, description))
    finally:
        in_file.close()

    # OK, we were able to parse the file; generate the C++ files

    def comparator(a, b):
        ak = a[2]
        bk = b[2]
        if ak == 0 and bk == 0:
            return cmp(a[0], b[0])
        elif ak == 0:
            return 1
        elif bk == 0:
            return -1
        else:
            return cmp(a[2], b[2])

    values.sort(comparator)
    value_map = dict((code, (name, description)) for name, _, code, description in values)
    max_code = max(value_map.iterkeys())

    current_year = datetime.date.today().year
    h_name = opts.output_prefix + '.h'
    cc_name = opts.output_prefix + '.cc'

    printable = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ '
    code_arr = []
    comment_width = 30
    for code in xrange(max_code + 1):
        if code and code in value_map:
            name, description = value_map[code]
            val = '      "%s",' % (name,)
            val += ' ' * (comment_width - len(val))
            val += '// %s' % (description,)
            code_arr.append(val)
        elif code < 128:
            chrval = chr(code)
            if chrval in printable:
                chrval = chrval.replace('\\', '\\\\')
                chrval = chrval.replace('"', '\\"')
                code_arr.append('      "%s",' % (chrval,))
            else:
                code_arr.append('      "\\x%02x",' % (code,))
            pass
        else:
            code_arr.append('      nullptr,')

    with open(h_name, 'w') as h_file:
        h_file.write(h_template.lstrip() % {'current_year': current_year})

    with open(cc_name, 'w') as cc_file:
        cc_file.write(cc_template.lstrip() % ({'arr_size': max_code + 1,
                                               'current_year': current_year,
                                               'codes': '\n'.join(code_arr),
                                               'h_name': os.path.basename(h_name),
                                               'max_code': max_code}))
