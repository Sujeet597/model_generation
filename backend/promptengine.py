def buildprompt(condition, gender, bodytype, pattern_name='none', color_name=None, view_direction="front"):
    
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
    - Season (summer, winter, festive, casual, formal)
    - Style (casual, party, ethnic, street, resort, winterwear)

    Then automatically choose the BEST outdoor fashion photoshoot environment:

    Rules:
    - Summer / resort wear → beach party, poolside, tropical vacation
    - Winter wear / jackets → snowy mountain station, winter street
    - Casual / streetwear → urban street, city road, graffiti wall
    - Ethnic / festive → palace, heritage fort, royal courtyard
    - Kidswear → park, playground, outdoor fun zone

    Pick ONLY ONE most suitable environment.
    Use natural outdoor lighting and lifestyle fashion photography look.
    The background must enhance the garment style and season.
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
    - {model_desc}
    - Confident neutral expression
    - Professional fashion pose

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
