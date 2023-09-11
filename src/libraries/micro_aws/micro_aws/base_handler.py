from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseLambdaHandler(ABC):
    def __call__(self, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Entry point of the order processing
        Reference:
            https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html
            https://docs.aws.amazon.com/lambda/latest/dg/python-context.html
        Args:
            event (Dict[str, Any]): the dictionary provided to the Lambda
                function as payload input
            context (object): Object that provides methods, properties and
                information about the invocation, function, and execution
                environment.
        Example:
        >>> # create the Handler
        >>> class NewHandler(BaseLambdaHandler):
        >>>     def __init__(...):
        >>>         ...
        >>>
        >>> if os.environ.get('AWS_EXECUTION_ENV'):
        >>>     lambda_handler = NewHandler()
        """
        return self.handle_request(event=event, context=context)

    @abstractmethod
    def handle_request(
        self,
        event: Dict[str, Any],
        context: Any,
        **kwargs: Any,
    ):
        """
        Entry point of the order processing, this differ from the __call__
        method only for the kwargs additional argument.
        In this way you have the chances to pass additional kwargs
        based on conditions/needs that we want to check outside the method
        Reference:
            https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html
            https://docs.aws.amazon.com/lambda/latest/dg/python-context.html
        Args:
            event (Dict[str, Any]): the dictionary provided to the Lambda
                function as payload input
            context (object): Object that provides methods, properties and
                information about the invocation, function, and execution
                environment.
            **kwargs (Any): the optional kwargs to be used as customization for
                particular handlers/order processing
        Example:
        >>> # create the NewHandler
        >>> class NewHandler(BaseLambdaHandler):
        >>>     def __init__(...):
        >>>         ...
        >>>
        >>> if os.environ.get('AWS_EXECUTION_ENV'):
        >>>     handler = NewHandler()
        >>>
        >>>     def lambda_handler(event: Dict[str, Any], context: object):
        >>>         handler.handle_request(event=event, context=context, special=True)
        """
