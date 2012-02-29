// -*- C++ -*-
// Copyright 2012, Evan Klitzke <evan@eklitzke.org>

#ifndef SRC_BUFFER_H_
#define SRC_BUFFER_H_

#include <string>
#include <vector>

#include "./line.h"

namespace e {
class Buffer {
 private:
  std::string filepath_;
  std::string name_;

  // cursor line and column
  int c_line_;
  int c_col_;

  bool dirty_;

 public:
  std::vector<e::Line> lines;

 public:
  // constructors
  explicit Buffer(const std::string &name);
  explicit Buffer(const std::string &name, const std::string &filepath);

  // get the name of the buffer
  const std::string & GetBufferName() const;

  // set the buffer name
  void SetBufferName(const std::string &);

  // get the number of lines in the buffer
  size_t Size() const;

  // is the buffer dirty?
  bool IsDirty(void) const;

};
}

#endif  // SRC_BUFFER_H_