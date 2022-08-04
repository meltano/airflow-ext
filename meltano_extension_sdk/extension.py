"""Meltano extension SDK base class and supporting methods."""
import json
from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import List

import yaml
from pydantic import BaseModel


class DescribeFormat(str, Enum):
    text = "text"
    json = "json"
    yaml = "yaml"


class Description(BaseModel):
    commands: List[str] = [":splat"]


class ExtensionBase(metaclass=ABCMeta):
    """Basic extension interface that must be implemented by all extensions."""

    def pre_invoke(self):
        """Called before the extension is invoked."""
        pass

    @abstractmethod
    def invoke(self) -> None:
        """Invoke method.

        This method is called when the extension is invoked.
        """
        pass

    def post_invoke(self):
        """Called after the extension is invoked."""
        pass

    @abstractmethod
    def describe(self) -> Description:
        """Describe method.

        This method should describe what commands & capabilities the extension provides.

        Returns:
            Description: A description of the extension.
        """
        pass

    def describe_formatted(
        self, output_format: DescribeFormat = DescribeFormat.text
    ) -> str:
        """Return a formatted description of the extensions commands and capabilities.

        Args:
            output_format: The output format to use.

        Returns:
            str: The formatted description.
        """

        meltano_config = {}
        for x in self.describe().commands:
            meltano_config[x] = f"invoke {x}"

        if output_format == DescribeFormat.text:
            return f"commands: {self.describe().commands}"
        elif output_format == DescribeFormat.json:
            return json.dumps({"commands": meltano_config}, indent=2)
        elif output_format == DescribeFormat.yaml:
            return yaml.dump({"commands": meltano_config})
