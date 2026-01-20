def buildprompt(condition, gender, bodytype, model, pattern_name='none', color_name=None, view_direction="front"):
    
    # MODEL DESCRIPTION
    match gender.lower() if gender else "":
        case 'male':          
            model_desc = "a professional male fashion model"
        case 'kid boy':
            model_desc = "a young boy model, age 8"
        case 'kid girl':
            model_desc = "a young girl model, age 8"
        case _:
            model_desc = "a professional female fashion model"

    # FRAMING
    match bodytype:
        case 'Full-Body':
            framing_desc = "full body fashion photoshoot, head to toe"
        case "Upper-Body":
            framing_desc = "upper body fashion photoshoot, waist up"
        case _:
            framing_desc = "lower body fashion photoshoot"

    # STRICT COLOR LOCK
    if color_name and isinstance(color_name, str):
        color_instr = (
            f"The garment color MUST be exactly {color_name}. "
            "No shade change. No variation. No recoloring. "
            "Preserve original fabric and texture."
        )
    else:
        color_instr = (
            "The garment color and pattern MUST be IDENTICAL to SOURCE_IMAGE. "
            "No color shift. No shade change. No pattern change."
        )

    # VIEW DIRECTION
    view_map = {
        "front": "Front-facing model pose showing the front of the garment clearly.",
        "back": "Back-facing model pose showing the back of the garment clearly.",
        "left side": "Left side profile model pose showing the side fit of the garment.",
        "closeup": "Close-up fashion shot highlighting fabric texture, stitching and details."
    }
    view_instr = view_map.get(view_direction.lower(), "Front-facing fashion model pose.")

    # AUTO BACKGROUND SELECTION (AI decides based on garment)
    background_instr = """
        FIRST analyze the SOURCE_IMAGE carefully.

        Identify:
        - Garment type (shirt, t-shirt, kurta, jacket, dress, kidswear, etc)
        - Garment fit and silhouette
        - Fabric texture and primary colors

        Then generate the final image in a professional photo studio setup.

        Background Rules:
        - Use a simple solid color studio background
        - Choose a neutral tone that complements the garment (white, off-white, light grey, beige, pastel)
        - No outdoor environment
        - No props, no scenery
        - No textures or patterns

        Lighting & Style:
        - Soft studio lighting
        - Clean even illumination
        - Subtle natural shadows
        - Professional fashion catalog photography look
        - Sharp focus on garment and fabric details

        Pick ONLY ONE best solid color background.
        The background must enhance the garment and keep the look minimal and premium.
        """


    # FINAL PROMPT
    prompt = f"""
    You are a world-class fashion photographer and AI fashion director.

    Your task:
    1. Analyze the SOURCE_IMAGE garment carefully.
    2. Understand the clothing type, season, and style.
    3. Select the best outdoor lifestyle fashion photoshoot environment.
    4. Generate a hyper-realistic fashion model photoshoot.

    Model:
    - model-type{model}
    - {model_desc}
    - Confident neutral expression
    - Professional fashion pose

    Size:
    -(2000x3000)px

    Framing:
    - {framing_desc}
    - {view_instr}

    Lighting:
    - Natural outdoor lighting
    - Cinematic fashion photography
    - Realistic fabric folds and shadows

    Background (AUTO-SELECTED BY AI):
    {background_instr}

    Garment Rules (STRICT):
    - {color_instr}
    - Preserve original pattern and fabric texture
    - No creative changes to garment

    Quality:
    - Ultra HD fashion photography
    - Marketplace catalog style (Myntra / Ajio / Zara)
    - Sharp focus, realistic rendering

    Output:
    - Professional fashion product image ready for e-commerce
    """

    return prompt
