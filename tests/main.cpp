// Test program for C++ counterpart.
//
// Compile with:
//
//    $ g++ main.cpp RunningStats.cpp RunningRegression.cpp
//
// Test with:
//
//    $ ./a.out 5 4 3 2 1
//    $ python -m tests 5 4 3 2 1
//

#include <stdio.h>
#include <string>

#include "RunningStats.h"
#include "RunningRegression.h"

int main(int argc, char ** argv)
{
  RunningStats stats = RunningStats();

  for (int index = 1; index < argc; index += 1)
    {
      double value = std::stod(std::string(argv[index]));
      stats.Push(value);
    }

  printf("Statistics\n");
  printf("Count: %lld\n", stats.NumDataValues());
  printf("Mean: %f\n", stats.Mean());
  printf("Variance: %f\n", stats.Variance());
  printf("StdDev: %f\n", stats.StandardDeviation());
  printf("Skewness: %f\n", stats.Skewness());
  printf("Kurtosis: %f\n", stats.Kurtosis());

  RunningRegression regr = RunningRegression();

  for (int index = 1; index < argc; index += 1)
    {
      double value = std::stod(std::string(argv[index]));
      regr.Push(index, value);
    }

  printf("\n");
  printf("Regression\n");
  printf("Count: %lld\n", regr.NumDataValues());
  printf("Slope: %f\n", regr.Slope());
  printf("Intercept: %f\n", regr.Intercept());
  printf("Correlation: %f\n", regr.Correlation());

  return 0;
}
