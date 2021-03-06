// -*- C++ -*-
// Copyright 2012, Evan Klitzke <evan@eklitzke.org>
//
// This file implements timers that are useful for implementing setTimeout() and
// setInterval().
//
// Each timer has a unique id (a 32 bit integer) that can be used
// to identify it. Timers can be cancelled by their id (which is used to
// implement clearTimeout() and clearInterval()).

#ifndef SRC_TIMER_H_
#define SRC_TIMER_H_

#include <boost/asio.hpp>
#include <v8.h>

using v8::Local;
using v8::Object;
using v8::ObjectTemplate;
using v8::Persistent;

namespace e {
class Timer {
 public:
  static Timer* New(Persistent<Object> callback) {
    return new Timer(callback);
  }

  ~Timer();

  // start the timer with a relative timeout
  void Start(uint32_t millis, bool repeat);

  // start the timer with an absolute timeout; never repeats
  void Start(uint64_t millis);

  // fire the timer
  bool Fire();

  // get the timer's id
  uint32_t GetId() const { return id_; }

 private:
  // Create a timer.
  explicit Timer(Persistent<Object> callback);

  Persistent<Object> func_;
  uint32_t id_;
  uint32_t millis_;
  bool repeat_;
  boost::asio::deadline_timer timer_;
};

// Cancel and delete all timers.
size_t CancelAllTimers();

// Add setTimeout(), setInterval(), clearTimeout(), and clearInterval() to the
// global template.
void AddTimersToGlobalNamespace(Local<ObjectTemplate> global);
}

#endif  // SRC_TIMER_H_
