from typing import List, Dict

import lark
from lark import ParseError
from overrides import overrides

from allennlp.training.metrics import Metric


@Metric.register("token_sequence_accuracy")
class TokenSequenceAccuracy(Metric):
    """
    Simple sequence accuracy based on tokens, as opposed to tensors.

    """

    def __init__(self) -> None:
        self._correct_counts = 0.
        self._total_counts = 0.

    @overrides
    def reset(self) -> None:
        self._correct_counts = 0.
        self._total_counts = 0.

    @overrides
    def __call__(self,
                 predictions: List[List[str]],
                 gold_targets: List[List[str]]) -> None:
        self._total_counts += len(predictions)
        for predicted_tokens, gold_tokens in zip(predictions, gold_targets):
            # If the whole sequence matches exactly, then we consider
            # it a hit.
            if predicted_tokens == gold_tokens:
                self._correct_counts += 1

    @overrides
    def get_metric(self, reset: bool = False) -> Dict[str, float]:
        if self._total_counts == 0:
            accuracy = 0.
        else:
            accuracy = self._correct_counts / self._total_counts

        if reset:
            self.reset()

        return {"seq_acc": accuracy}

@Metric.register("intent_slot_accuracy")
class IntentSlotAccuracy(Metric):
    """
    Simple sequence accuracy based on tokens, as opposed to tensors.

    """

    def __init__(self) -> None:
        self._correct_intent_counts = 0.
        self._correct_slot_counts = 0.
        self._total_counts = 0.

    @overrides
    def reset(self) -> None:
        self._correct_intent_counts = 0.
        self._correct_slot_counts = 0.
        self._total_counts = 0.

    @overrides
    def __call__(self,
                 predictions: List[List[str]],
                 gold_targets: List[List[str]]) -> None:
        self._total_counts += len(predictions)
        for predicted_tokens, gold_tokens in zip(predictions, gold_targets):
            if predicted_tokens[0] == gold_tokens[0]:
                self._correct_intent_counts += 1
            if predicted_tokens[1:] == gold_tokens[1:]:
                self._correct_slot_counts += 1

    @overrides
    def get_metric(self, reset: bool = False) -> Dict[str, float]:
        if self._total_counts == 0:
            intent_accuracy = 0.
            slot_accuracy = 0.
        else:
            intent_accuracy = self._correct_intent_counts / self._total_counts
            slot_accuracy = self._correct_slot_counts / self._total_counts

        if reset:
            self.reset()

        return {"intent_acc": intent_accuracy,
                "slot_acc": slot_accuracy}

@Metric.register("valid_parse")
class ParseValidity(Metric):
    """
    Simple sequence accuracy based on tokens, as opposed to tensors.

    """

    def __init__(self, parser) -> None:
        self._correct_counts = 0.
        self._total_counts = 0.
        self._parser = parser

    @overrides
    def reset(self) -> None:
        self._correct_counts = 0.
        self._total_counts = 0.

    @overrides
    def __call__(self,
                 predictions: List[List[str]],
                 gold_targets: List[List[str]]) -> None:
        self._total_counts += len(predictions)
        for predicted_tokens in predictions:
            as_str = " ".join(predicted_tokens)
            try:
                self._parser.parse(as_str)
                self._correct_counts += 1
            except lark.exceptions.LarkError:
                continue

    @overrides
    def get_metric(self, reset: bool = False) -> Dict[str, float]:
        if self._total_counts == 0:
            accuracy = 0.
        else:
            accuracy = self._correct_counts / self._total_counts

        if reset:
            self.reset()

        return {"parse_validity": accuracy}