import numpy as np
from ..base import BaseOptimizer, Parameter


def tpe_build_posterior_parameter(parameter, observations):
    """TPE algorith transform a prior parameter into a posterior parameters using observations
    to build posterior.
    """
    posterior_parameter = None
    parameter_values = [observation.sample[parameter.name] for observation in observations]
    search_space = parameter.search_space
    if parameter.category == "categorical":
        prior_weights = np.array(search_space["weights"])
        posterior_weights = prior_weights
        if len(parameter_values) != 0:
            observed_weights = np.array([parameter_values.count(value)
                                         for value in search_space["values"]])
            observed_weights = observed_weights / np.sum(observed_weights)
            posterior_weights += observed_weights
            posterior_weights /= sum(posterior_weights)

        # Build param
        posterior_parameter = Parameter.from_dict(
            {
                "name": parameter.name,
                "category": "categorical",
                "search_space": {
                    "values": search_space["values"],
                    "weights": list(posterior_weights),
                }
            }
        )

    if parameter.category in ("uniform", "normal"):
        if parameter.category == "uniform":
            prior_mu = 0.5 * (search_space["high"] + search_space["low"])
            prior_sigma = (search_space["high"] - search_space["low"])
        elif parameter.category == "normal":
            prior_mu = search_space["mu"]
            prior_sigma = search_space["sigma"]

        # Mus
        mus = np.sort(parameter_values + [prior_mu])

        # Sigmas
        # Trick to get for each mu the greater distance from left and right neighbor
        # when low and high are not defined we use inf to get the only available distance
        # (right neighbor for sigmas[0] and left for sigmas[-1])
        tmp = np.concatenate(
            (
                [search_space.get("low", np.inf)],
                mus,
                [search_space.get("high", -np.inf)],
            )
        )
        sigmas = np.maximum(tmp[1:-1] - tmp[0:-2], tmp[2:] - tmp[1:-1])

        # Use formulas from hyperopt to clip sigmas
        sigma_max_value = prior_sigma
        sigma_min_value = prior_sigma / min(100.0, (1.0 + len(mus)))
        sigmas = np.clip(sigmas, sigma_min_value, sigma_max_value)

        # Fix prior sigma with correct value
        sigmas[np.where(mus == prior_mu)[0]] = prior_sigma

        posterior_parameter = Parameter.from_dict(
            {
                "name": parameter.name,
                "category": "gaussian_mixture",
                "search_space": {
                    "mus": list(mus),
                    "sigmas": list(sigmas),
                    "low": search_space["low"],
                    "high": search_space["high"],
                    "log": search_space.get("log", False),
                    "step": search_space.get("step", None)
                }
            }
        )

    return posterior_parameter


class TPE(BaseOptimizer):

    def __init__(self,
                 optimization_problem,
                 gamma=0.15,
                 number_of_candidates=100,
                 max_retry=5):
        super(TPE, self).__init__(optimization_problem)
        self.gamma = gamma
        self.number_of_candidates = number_of_candidates

    def _generate_sample(self):
        # Retrieve self.gamma % best observations (lowest loss) observations_l
        # and worst obervations (greatest loss g) observations_g
        observations_l, observations_g = self.optimization_problem.observations_quantile(
            self.gamma)

        # Build a sample going through every parameters
        sample = {}
        for parameter in self.parameters:

            posterior_parameter_l = tpe_build_posterior_parameter(parameter, observations_l)
            posterior_parameter_g = tpe_build_posterior_parameter(parameter, observations_g)

            # Draw candidates from observations_l
            candidates = posterior_parameter_l.draw(self.number_of_candidates)

            # Evaluate cantidates score according to g / l taking care of zero division
            scores = (posterior_parameter_g.pdf(candidates) /
                      np.clip(posterior_parameter_l.pdf(candidates),
                              a_min=1e-16,
                              a_max=None))

            sample[parameter.name] = candidates[np.argmin(scores)]
        return sample

    def suggest(self):
        return self._generate_sample()