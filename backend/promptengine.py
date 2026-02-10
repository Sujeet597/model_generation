def buildprompt(condition, gender, bodytype, model, image_count, pattern_name='none',  broach_placement=None, special_instructions=None, color_name=None, view_direction="front"):
    
    # MODEL DESCRIPTION
    print(image_count)
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
    if image_count == "1":
        view_map = {
            "front": "Front-facing model pose showing the front of the garment clearly."
        }
        print("Single image requested, using front view only.")
    
    else:
        view_map = {
            "front": "Front-facing model pose showing the front of the garment clearly.",
            "back": "Back-facing model pose showing the back of the garment clearly.",
            "left side": "Left side profile model pose showing the side fit of the garment.",
            "closeup": "Close-up fashion shot highlighting fabric texture, stitching and details."
        }
        print("Multiple images requested, using all views.")
    view_instr = view_map.get(view_direction.lower(), "Front-facing fashion model pose.")
    if broach_placement:
        view_instr += f" The broach should be prominently displayed on the {broach_placement} of the garment."
    else:
        view_instr += " No broach is to be included in the image."
    if special_instructions:
        view_instr += f" Additional instructions: {special_instructions}"
    else:
        view_instr += " No additional special instructions."

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

    PRIMARY OBJECTIVE:
    Generate a hyper-realistic fashion photoshoot image by strictly preserving
    the garment from the SOURCE_IMAGE.

    STEP-BY-STEP TASK:
    1. Carefully analyze the SOURCE_IMAGE garment.
    2. Identify exact clothing type, fit, fabric, pattern, and construction.
    3. Select a realistic outdoor lifestyle fashion environment that MATCHES the garment season and style.
    4. Generate a professional e-commerce fashion photoshoot.

    IMPORTANT CONDITIONS:
    - Special instruction: {special_instructions or "None"}
    PRODUCT TAG / BROOCH INSTRUCTIONS (STRICT):
        - Type: { "Product tag" or "Brooch" }
        - Visibility: Clearly visible but non-distracting
        - Placement: {broach_placement or "N/A"}
        - Attachment method:
        - Product tag: Thin string / safety pin / fabric loop
        - Brooch: Properly pinned, flat against fabric
        - Size: Small, proportional to garment
        - Color: Neutral (white / beige / metallic) unless specified
        - Must look physically attached (not floating)
        - Must NOT alter garment shape, fit, or drape
        - No additional accessories allowed


    MODEL DETAILS (STRICT):
    - Model type: {model}
    - Description: {model_desc}
    - Expression: Neutral, confident
    - Pose: Professional fashion pose
    - Body posture must not distort garment fit

    IMAGE SIZE (STRICT — DO NOT CHANGE):
    - Final output size: 2:3 aspect ratio
    - Aspect ratio: Preserved 
    - Garment: Rendered at natural size and proportions (no upscaling/downscaling)
    - If needed, add clean padding/negative space to fit the canvas
    - Center the model/garment on the canvas
    - Any source ratio is fine, but final canvas will be exactly 2:3 ratio with the garment properly scaled and centered

    FRAMING & CAMERA:
    - Framing: {framing_desc}
    - View: {view_instr}
    - Full garment must be visible (no cropping unless specified)

    LIGHTING:
    - Natural outdoor lighting
    - Soft cinematic fashion light
    - Accurate fabric shadows and folds
    - No harsh highlights or artificial glow

    BACKGROUND (AI-SELECTED BUT CONTROLLED):
    - {background_instr}
    - Background must NOT distract from garment
    - Depth of field must keep garment sharp

    GARMENT PRESERVATION RULES (ABSOLUTE):
    - Color: {color_instr}
    - Fabric texture must remain unchanged
    - Pattern must remain identical
    - Stitching, cut-outs, brooch, and design details must match SOURCE_IMAGE
    - NO redesign, NO styling alteration, NO added accessories

    QUALITY STANDARD:
    - Ultra-HD realism
    - Marketplace catalog quality (Myntra / Ajio / Zara)
    - Clean, sharp, commercial-ready output

    FINAL OUTPUT:
    - One professional fashion product image
    - Ready for e-commerce listing
    """


    return prompt
