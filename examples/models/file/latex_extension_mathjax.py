import numpy as np
from scipy.special import jv

from bokeh.models import Label
from bokeh.palettes import Spectral4
from bokeh.core.properties import (
  Nullable,
  Float
)
from bokeh.plotting import figure, output_file, show
from bokeh.util.compiler import TypeScript

output_file('latex_extension_with_mathjax.html')

class LatexLabel(Label):
    width = Nullable(Float, help="""
    The gradient of the line, in data units
    """)
    height = Nullable(Float, help="""
    The gradient of the line, in data units
    """)
    """A subclass of `Label` with all of the same class attributes except
    canvas mode isn't supported and DOM manipulation happens in the TypeScript
    superclass implementation that requires setting `render_mode='css'`).

    Only the render method of LabelView is overwritten to perform the
    text -> latex (via MathJax) conversion
    """
    __javascript__ = ["https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"]
    __implementation__ = TypeScript("""
import {Label, LabelView} from "models/annotations/label"
import * as p from "core/properties"

declare namespace MathJax {
  function tex2svg(input: string): any
}

export class LatexLabelView extends LabelView {
  model: LatexLabel

  protected _render(): void {
    const panel = this.layout != null ? this.layout : this.plot_view.frame

    const xscale = this.coordinates.x_scale
    const yscale = this.coordinates.y_scale

    let sx = this.model.x_units == "data" ? xscale.compute(this.model.x) : panel.bbox.xview.compute(this.model.x)
    let sy = this.model.y_units == "data" ? yscale.compute(this.model.y) : panel.bbox.yview.compute(this.model.y)

    sx += this.model.x_offset
    sy -= this.model.y_offset

    const svgElement = MathJax.tex2svg(this.model.text).children[0]

    let outerHTML = svgElement.outerHTML,
      blob = new Blob([outerHTML],{type:'image/svg+xml;charset=utf-8'});

    let URL = window.URL || window.webkitURL || window;
    let blobURL = URL.createObjectURL(blob);

    let image = new Image();

    image.onload = () => {
      this.layer.ctx.drawImage(image, sx, sy, this.model.width, this.model.height);
    };

    image.src = blobURL;
  }
}

export namespace LatexLabel {
  export type Attrs = p.AttrsOf<Props>

  export type Props = Label.Props & {
    width: p.Property<number>
    height: p.Property<number>
  }
}

export interface LatexLabel extends LatexLabel.Attrs {}

export class LatexLabel extends Label {
  properties: LatexLabel.Props
  __view_type__: LatexLabelView

  static init_LatexLabel(): void {
    this.prototype.default_view = LatexLabelView

    this.define<LatexLabel.Props>(({Number}) => ({
      width: [ Number ],
      height: [ Number ],
    }))
  }
}
""")

p = figure(title="LaTex Extension Demonstration", plot_width=800, plot_height=350,
           background_fill_color="#fafafa")
p.x_range.range_padding = 0

x = np.arange(0.0, 20.0, 0.02)

for i, n in enumerate([0, 1, 4, 7]):
    p.line(x, jv(n, x), line_width=3, color=Spectral4[i], alpha=0.8, legend_label="𝜈=%d" % n)

text = ("x = {-b \pm \sqrt{b^2-4ac} \over 2a}")

latex = LatexLabel(text=text,x=4.5, y=250, x_units='data', y_units='screen',
                   render_mode='css', text_font_size='11px', width=300, height=75,
                   background_fill_color="white", border_line_color="lightgrey")

p.add_layout(latex)

show(p)
