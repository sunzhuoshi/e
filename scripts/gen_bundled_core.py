import datetime
import optparse
import pprint
import sys
import urllib
import urllib2
import json

h_template = """
// -*- C++ -*-
// Copyright %(current_year)d, Evan Klitzke <evan@eklitzke.org>
//
// This is the header file for the C++ representation of the "core" JavaScript
// code. This exists so that we can have a safe representation of the core code,
// and ship a working binary without any extra files.
//
// This file is AUTOGENERATED by gen_bundled_core.py, do not edit by hand!

#ifndef SRC_BUNDLED_CORE_H_
#define SRC_BUNDLED_CORE_H_

#include <v8.h>

namespace e {
v8::Local<v8::Script> GetCoreScript();
}
#endif  // SRC_BUNDLED_CORE_H_"""

cc_template = """
// -*- C++ -*-
// Copyright %(current_year)d, Evan Klitzke <evan@eklitzke.org>
//
// This file is AUTOGENERATED by gen_bundled_core.py, do not edit by hand!

#include <v8.h>

namespace e {
// This is the "minified" core.js code, as a C string. The reason for
// obfuscating it like this is simply to avoid having to escape the string in a
// way that's safe for C. Python's built in "string_escape" codec comes close
// but doesn't quite grok C.
static const char *core_src = (
%(split_src)s);

v8::Local<v8::Script> GetCoreScript() {
  v8::HandleScope scope;
  v8::Local<v8::String> src = v8::String::New(core_src);
  v8::Local<v8::String> src_name = v8::String::New("core.js");
  v8::Local<v8::Script> script = v8::Script::New(src, src_name);
  return scope.Close(script);
}
}"""

def get_compiled_code(input_files):
    code = []
    for filename in input_files:
        with open(filename) as f:
            code.append(f.read())
    request_params = [
        ('js_code', '\n'.join(code)),
        ('compilation_level', 'SIMPLE_OPTIMIZATIONS'),
        ('output_format', 'json'),
        ('output_info', 'compiled_code'),
        ('output_info', 'errors'),
        ('exclude_default_externs', 'true')
        ]
    if opts.warnings:
        request_params.append(('output_info', 'warnings'))
    if opts.statistics:
        request_params.append(('output_info', 'statistics'))
    
    r = urllib.urlopen('https://closure-compiler.appspot.com/compile', urllib.urlencode(request_params))
    response = json.load(r)
    if 'warnings' in response:
        print 'WARNINGS'
        print '=============='
        print pprint.pprint(response['warnings'])
        sys.exit(1)
    if 'errors' in response:
        print 'ERRORS'
        print '=============='
        print pprint.pprint(response['errors'])
        sys.exit(1)
    if 'statistics' in response:
        print 'STATISTICS'
        print '=============='
        print pprint.pprint(response['statistics'])

    return response['compiledCode']


def write_output(code, output):
    current_year = datetime.date.today().year

    # add a copyright header to the minified JS
    hdr = '// Copyright %d, Evan Klitzke <evan@eklitzke.org>' % current_year
    code = hdr + '\n' + code

    line_size = 18
    splitsrc = []
    while code:
        splitsrc.append(code[:line_size])
        code = code[line_size:]

    escaped_output = []
    for line in splitsrc:
        l = '"%s"' % ''.join('\\x%02x' % ord(c) for c in line)
        escaped_output.append(l)

    splitsrc = '  ' + '\n  '.join(escaped_output)
    cc_src = cc_template.strip() % {
        'current_year': current_year,
        'split_src': splitsrc
        }
    h_src = h_template.strip() % {'current_year': current_year}

    with open(output + '.h', 'w') as h:
        h.write(h_src + '\n')
    with open(output + '.cc', 'w') as cc:
        cc.write(cc_src + '\n')


if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-f', '--file', dest='files', default=[], action='append', help='The files to use')
    parser.add_option('--no-warnings', dest='warnings', default=True, action='store_false', help='Get warnings')
    parser.add_option('-s', '--statistics', action='store_true', help='Get statistics')
    parser.add_option('-o', '--outfile', default='src/bundled_core', help='Output file to emit')
    opts, args = parser.parse_args()
    if not opts.outfile:
        parser.error('must have an outfile')
        sys.exit(1)

    code = get_compiled_code(opts.files or ['js/core.js'])
    write_output(code, opts.outfile)
