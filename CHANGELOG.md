# Changelog

## 1.0.1

First public release of the converter, including the spruce inventory tint fix.

The earlier local-only port omitted the constant green tint from spruce leaf
item definitions, causing gray/yellow inventory icons while placed leaves
remained correct. This version preserves Minecraft 26.3's spruce item tint
and continues to leave the authored birch leaf colors untinted.

Includes the existing 26.3 resource-path, sign UV, model and Continuity rule
conversions. No original or generated texture-pack ZIP is included.
