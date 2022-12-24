import os
import sympy
import discord
import numpy as np
from io import BytesIO
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

bot = discord.Bot(intents=discord.Intents.all())

plot_grp = discord.SlashCommandGroup("plot", "Plotting Tools")

bot.add_application_command(plot_grp)

@bot.event
async def on_ready():
    print(f'{bot.user} is ready and online!')

@plot_grp.command(description = "Single plot for your function")
async def single(ctx, function: discord.Option(str), range_min: discord.Option(float), range_max: discord.Option(float)):
    # Parse the string to get the sympy function
    x = sympy.Symbol('x')
    try:
        y = sympy.sympify(function)
    except sympy.SympifyError:
        await ctx.respond("Could not parse your function please refer to our documentation.")
        return

    # Generate a numpy-compatible function from the sympy expression
    f = sympy.lambdify(x, y, 'numpy')

    # Generate a sequence of x values from range_min to range_max
    x_values = np.linspace(range_min, range_max, 100)

    # Evaluate the function for each x value
    y_values = f(x_values)

    # Create a FigureCanvas object
    canvas = FigureCanvas(plt.gcf())

    # Plot the graph of f(x)
    plt.plot(x_values, y_values)

    # Add labels to the x-axis and y-axis
    plt.xlabel("x")
    plt.ylabel("f(x)")

    # Add a title to the plot
    plt.title(f"Graph of {function}")

    # Convert the plot to a png image and store it in a BytesIO object
    canvas = FigureCanvas(plt.gcf())
    buf = BytesIO()
    canvas.print_png(buf)

    # Get the png image as a binary stream
    image = buf.getvalue()

    # Create a file-like object from the image data
    image_file = BytesIO(image)

    # Send the image to the Discord chat
    await ctx.respond(f"Here is the graph of f(x) = {y} in the range of {range_min}-{range_max}")
    await ctx.send(file=discord.File(image_file, 'plot.png'))

try:
    bot.run(TOKEN)
except discord.HTTPException as e:
   if e.status == 429: #rate limited: too much connecions
      os.system("restarter.py")
      os.system("kill 1")
