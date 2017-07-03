// Copied from https://www.johndcook.com/blog/running_regression/

#include "RunningRegression.h"

RunningRegression::RunningRegression()
{
    Clear();
}

void RunningRegression::Clear()
{
    x_stats.Clear();
    y_stats.Clear();
    S_xy = 0.0;
    n = 0;
}

void RunningRegression::Push(double x, double y)
{
    S_xy += (x_stats.Mean() -x)*(y_stats.Mean() - y)*double(n)/double(n+1);

    x_stats.Push(x);
    y_stats.Push(y);
    n++;
}

long long RunningRegression::NumDataValues() const
{
    return n;
}

double RunningRegression::Slope() const
{
    double S_xx = x_stats.Variance()*(n - 1.0);

    return S_xy / S_xx;
}

double RunningRegression::Intercept() const
{
    return y_stats.Mean() - Slope()*x_stats.Mean();
}

double RunningRegression::Correlation() const
{
    double t = x_stats.StandardDeviation() * y_stats.StandardDeviation();
    return S_xy / ( (n-1) * t );
}

RunningRegression operator+(const RunningRegression a, const RunningRegression b)
{
    RunningRegression combined;

    combined.x_stats = a.x_stats + b.x_stats;
    combined.y_stats = a.y_stats + b.y_stats;
    combined.n = a.n + b.n;

    double delta_x = b.x_stats.Mean() - a.x_stats.Mean();
    double delta_y = b.y_stats.Mean() - a.y_stats.Mean();
    combined.S_xy = a.S_xy + b.S_xy +
    double(a.n*b.n)*delta_x*delta_y/double(combined.n);

    return combined;
}

RunningRegression& RunningRegression::operator+=(const RunningRegression &rhs)
{
    RunningRegression combined = *this + rhs;
    *this = combined;
    return *this;
}
