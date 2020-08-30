#ifndef STOPWATCH_H
#define STOPWATCH_H

#include <chrono>
#include <iostream>
#include <string>

struct Sec
{
    using Unit = std::chrono::seconds;
    static const std::string unit;
};
const std::string Sec::unit = "s";

struct MilliSec
{
    using Unit = std::chrono::milliseconds;
    static const std::string unit;
};
const std::string MilliSec::unit = "ms";

struct MicroSec
{
    using Unit = std::chrono::microseconds;
    static const std::string unit;
};
const std::string MicroSec::unit = "us";

struct NanoSec
{
    using Unit = std::chrono::nanoseconds;
    static const std::string unit;
};
const std::string NanoSec::unit = "ns";

template <typename ClockType, typename UnitType>
class StopWatch
{
  public:
    StopWatch() = delete;
    StopWatch(const StopWatch&) = delete;
    StopWatch(StopWatch&&) = delete;

    StopWatch& operator=(const StopWatch&) = delete;
    StopWatch& operator=(StopWatch&&) = delete;

    StopWatch(const std::string& info = "", std::ostream& os = std::cout) : os_(os), info_(info)
    {
        start_ = ClockType::now();
    }

    ~StopWatch()
    {
        if (paused_)
        {
            Resume();
        }

        auto end = ClockType::now();
        if (!manual_ended_)
        {
            const auto duration = std::chrono::duration_cast<typename UnitType::Unit>(end - start_);
            os_ << info_ << ": " << (duration.count() + elapsed_) << UnitType::unit << ".\n";
        }
    }

    void ManualStart() { start_ = ClockType::now(); }

    void ManualStop()
    {
        if (paused_)
        {
            Resume();
        }
        auto end = ClockType::now();
        const auto duration = std::chrono::duration_cast<typename UnitType::Unit>(end - start_);
        os_ << info_ << ": " << (duration.count() + elapsed_) << UnitType::unit << ".\n";

        manual_ended_ = true;
    }

    void ManualStop(std::ostream& os)
    {
        if (paused_)
        {
            Resume();
        }
        auto end = ClockType::now();
        const auto duration = std::chrono::duration_cast<typename UnitType::Unit>(end - start_);
        os << info_ << ": " << (duration.count() + elapsed_) << UnitType::unit << ".\n";

        manual_ended_ = true;
    }

    void Pause()
    {
        auto end = ClockType::now();
        const auto duration = std::chrono::duration_cast<typename UnitType::Unit>(end - start_);
        elapsed_ += duration.count();
    }

    void Resume() { start_ = ClockType::now(); }

    void Reset()
    {
        elapsed_ = 0;
        manual_ended_ = false;
        paused_ = false;
        start_ = ClockType::now();
    }

    void Reset(const std::string& info)
    {
        info_ = info;

        elapsed_ = 0;
        manual_ended_ = false;
        paused_ = false;
        start_ = ClockType::now();
    }

    void Reset(const std::string& info, std::ostream& os)
    {
        os_ = os;
        info_ = info;

        elapsed_ = 0;
        manual_ended_ = false;
        paused_ = false;
        start_ = ClockType::now();
    }

  private:
    std::ostream& os_;
    std::string info_;
    bool manual_ended_{false};
    bool paused_{false};

    typename ClockType::time_point start_;
    typename ClockType::rep elapsed_{0};
};

using SecStopWatch = StopWatch<std::chrono::high_resolution_clock, Sec>;
using MilliSecStopWatch = StopWatch<std::chrono::high_resolution_clock, MilliSec>;
using MicroSecStopWatch = StopWatch<std::chrono::high_resolution_clock, MicroSec>;
using NanoSecStopWatch = StopWatch<std::chrono::high_resolution_clock, NanoSec>;

#endif  // STOPWATCH_H