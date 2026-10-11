// 1. Select all annotations (including your imported GeoJSON shapes)
def annotations = getAnnotationObjects()

// 2. Resolve relationships so cells become children of overlapping annotations
resolveHierarchy()

// 3. Optional: Filter out detections that fell outside your target training zones
def targetClass = getPathClass("Your_Training_Class") // Change to your class name

annotations.each { annotation ->
    if (annotation.getPathClass() == targetClass) {
        // All cells inside this annotation inherit the classification for training
        annotation.getChildObjects().each { child ->
            if (child.isDetection()) {
                child.setPathClass(targetClass)
            }
        }
    }
}

// 4. Refresh the viewer and object hierarchy
fireHierarchyUpdate()