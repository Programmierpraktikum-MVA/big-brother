import face_recognition_strategies.strategies.base_strategy

class Context:
    def __init__(self, strategy):
        """
        Initializes the strategy.

        Arguments:
        strategy -- The strategy to be set.

        Exceptions:
        ValueError -- Raises exception is the argument doesn't inherit from base_strategy.
        """
        set_strategy(strategy)

    def set_strategy(self, strategy):
        """
        Set the strategy.

        Arguments:
        strategy -- The strategy to be set.

        Exceptions:
        ValueError -- Raises exception is the argument doesn't inherit from base_strategy.
        """
        self._check_is_strategy()
        self.strategy = strategy

    def _check_is_strategy(self, strategy):
        """
        Checks whether argument inherits fom base_strategy and raises exception otherwise.

        Arguments:
        strategy -- Variable to check.

        Exceptions:
        ValueError -- Raises exception is the argument doesn't inherit from base_strategy.
        """
        if not issubclass(strategy, base_strategy):
            raise ValueError(f"Face recognition strategy expected, but '{type(strategy)}' found")

    def execute_strategy(self, data_train, data_test):
        """
        Executes the strategy that has been set with the given data.
        """
        data_train, data_test = self.strategy.preprocess_data(data_train, data_test)
        return self.strategy(data_train, data_test)
