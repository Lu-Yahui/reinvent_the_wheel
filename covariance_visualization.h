#include <cmath>

#include <eigen3/Eigen/Core>
#include <eigen3/Eigen/Dense>

template <int N = 36, typename T = double>
Eigen::Matrix<T, 2, N> CovariancePoints(const Eigen::Matrix<T, 2, 1>& mean, const Eigen::Matrix<T, 2, 2>& cov)
{
    Eigen::EigenSolver<Eigen::Matrix<T, 2, 2>> eigen_solver;
    eigen_solver.compute(cov);
    Eigen::Matrix<T, 2, 1> eigen_values = eigen_solver.eigenvalues().real();
    Eigen::Matrix<T, 2, 2> eigen_vectors = eigen_solver.eigenvectors().real();

    int big_index = 0;
    int small_index = 1;

    if (eigen_values(0, 0) < eigen_values(1, 0))
    {
        big_index = 1;
        small_index = 0;
    }

    T a = std::sqrt(eigen_values(big_index, 0));
    T b = std::sqrt(eigen_values(small_index, 0));
    T step = 2.0 * M_PI / (N - 1);

    Eigen::Matrix<T, 2, N> points;
    for (int i = 0; i < N; ++i)
    {
        T sample_angle = i * step;

        T x = a * std::cos(sample_angle);
        T y = b * std::sin(sample_angle);

        T angle = std::atan2(eigen_vectors(big_index, 1), eigen_vectors(big_index, 0));

        points(0, i) = x * std::cos(angle) + y * std::sin(angle) + mean(0, 0);
        points(1, i) = -x * std::sin(angle) + y * std::cos(angle) + mean(1, 0);
    }

    return points;
}
