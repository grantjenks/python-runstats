// Copied from https://www.johndcook.com/blog/running_regression/

#ifndef RUNNINGREGRESSION
#define RUNNINGREGRESSION

#include "RunningStats.h"

class RunningRegression
{
    public:
        RunningRegression();
        void Clear();
        void Push(double x, double y);
        long long NumDataValues() const;
        double Slope() const;
        double Intercept() const;
        double Correlation() const;

    friend RunningRegression operator+(
    const RunningRegression a, const RunningRegression b);
    RunningRegression& operator+=(const RunningRegression &rhs);

    private:
        RunningStats x_stats;
        RunningStats y_stats;
        double S_xy;
        long long n;
};

#endif
