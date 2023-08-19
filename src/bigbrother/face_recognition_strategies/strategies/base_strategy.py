from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    """
    Defines common interface that all face recognition strategies have in
    common.
    """

    @abstractmethod
    def execute(self, data_train, data_test):
        """
        Executes the strategy.

        Arguments:
        data_train -- List of training data.
        data_test -- List of test data.

        Return:
        Returns True if the test data matches with the training data and 
        False otherwise.
        """
        pass

    @abstractmethod
    def preprocess_training_data(self, data_train):
        """
        This method converts list of data (mostly images) into correct format 
        for algorithm to work. This method is specifically called on the 
        training data.

        This might be the case if data have another format in one section of 
        the code and therefore need to be converted. You
        may also implement different data processors/converters.

        Arguments:
        data_train -- List with training data. 

        Return:
        List of processed training data.
        """
        pass

    @abstractmethod
    def preprocess_testing_data(self, data_test):
        """
        This method converts list of data (mostly images) into correct format 
        for algorithm to work. This method is specifically called on the 
        testing data.

        This might be the case if data have another format in one section of 
        the code and therefore need to be converted. You
        may also implement different data processors/converters.

        Arguments:
        data_test -- List with testing data.

        Return:
        List of processed testing data.
        """
        pass
