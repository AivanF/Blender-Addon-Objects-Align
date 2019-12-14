__author__ = 'AivanF'
__copyright__ = 'Copyright 2019, AivanF'
__contact__ = 'projects@aivanf.com'

import bpy


bl_info = {
    'name': 'Align objects',
    'description': 'Allows to align selected object in various ways',
    'author': 'AivanF',
    'version': (1, 1,),
    'blender': (2, 65, 0),
    'category': 'Object',
    'location': 'View3D > Object > Align',
    'warning': '',
    'support': 'Development',
    'wiki_url': 'https://github.com/AivanF/Blender-Addon-Objects-Align',
}

NAME = 'Align objects'
DESCRIPTION = 'Allows to align selected object in various ways'

ITEMS = [
    ('x', 'X', 'X axis'),
    ('y', 'Y', 'Y axis'),
    ('z', 'Z', 'Z axis'),
]

AXIS_INDICES = {'x': 0, 'y': 1, 'z': 2}

PROPERTY_FROM = bpy.props.EnumProperty(name='Source', default='x', items=ITEMS)
PROPERTY_TO = bpy.props.EnumProperty(name='Target', default='x', items=ITEMS)
PROPERTY_PADDING_TYPE = bpy.props.EnumProperty(name='Padding type', default='c', items=[
    ('c', 'Centers', 'Centers'),
    ('b', 'Borders', 'Borders'),
])


def position_metagetter(attr):
    """Returns function for getting object's location by given axis"""
    def getter(obj):
        return getattr(obj.location, attr)
    return getter


def dimension_metagetter(attr):
    """Returns function for getting object's dimension by given axis"""
    def getter(obj):
        return getattr(obj.dimensions, attr)
    return getter


def get_sorted_selected(context, axis):
    return list(sorted(
        context.selected_objects,
        key=position_metagetter(axis)
    ))


class OBJECT_OT_align_bounds(bpy.types.Operator):
    bl_idname = 'object.align_bounds'
    bl_label = 'Align between bounds'
    bl_description = 'Align objects equidistantly \
between most distant objects \
along one axis with order from another axis'
    bl_options = {'REGISTER', 'UNDO'}

    axis_from = PROPERTY_FROM
    axis_to = PROPERTY_TO
    padding_type = PROPERTY_PADDING_TYPE

    def execute(self, context):
        # Save relative order
        ordered_objects = get_sorted_selected(context, self.axis_from)
        position_getter = position_metagetter(self.axis_to)
        dimension_getter = dimension_metagetter(self.axis_to)

        positions = list(map(position_getter, ordered_objects))
        mn = min(positions)
        mx = max(positions)
        cnt = len(ordered_objects)
        if cnt < 2:
            return {'CANCELLED'}

        # Regulate order
        if self.padding_type == 'c':
            for i, obj in enumerate(ordered_objects):
                location = mn * (cnt - i - 1) / (cnt - 1) + mx * i / (cnt - 1)
                setattr(obj.location, self.axis_to, location)
            return {'FINISHED'}

        elif self.padding_type == 'b':
            dimensions = list(map(dimension_getter, ordered_objects))
            dim_total = sum(dimensions) - dimensions[0]/2 - dimensions[-1]/2
            space_total = mx - mn
            free_space = space_total - dim_total
            gap = free_space / (cnt - 1)
            
            for i in range(1, cnt-1):
                obj = ordered_objects[i]
                prev = ordered_objects[i-1]
                location = positions[i-1] + dimensions[i-1] / 2 + dimensions[i] / 2 + gap
                setattr(obj.location, self.axis_to, location)
                positions[i] = location

        else:
            raise ValueError('Unknown padding type %s' % self.padding_type)

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class OBJECT_OT_align_padding(bpy.types.Operator):
    bl_idname = 'object.align_padding'
    bl_label = 'Specific padding by cursor'
    bl_description = 'Align objects equidistantly \
with given padding at cursor location \
along one axis with order from another axis'
    bl_options = {'REGISTER', 'UNDO'}

    axis_from = PROPERTY_FROM
    axis_to = PROPERTY_TO
    padding_type = PROPERTY_PADDING_TYPE
    padding = bpy.props.FloatProperty(name="Padding", default=1)
    placement = bpy.props.EnumProperty(name='Direction', default='p', items=[
        ('p', 'Positive', 'Place objects on positive direction'),
        ('c', 'Centered', 'Place objects around cursor'),
        ('n', 'Negative', 'Place objects on negative direction'),
    ])

    def execute(self, context):
        # Save relative order
        ordered_objects = get_sorted_selected(context, self.axis_from)
        dimension_getter = dimension_metagetter(self.axis_to)

        # Regulate order
        if bpy.app.version < (2, 80, 0):
            initial = bpy.context.scene.cursor_location[AXIS_INDICES[self.axis_to]]
        else:
            initial = bpy.context.scene.cursor.location[AXIS_INDICES[self.axis_to]]
        cnt = len(ordered_objects)

        # Regulate order
        if self.padding_type == 'c':
            shift = 0
            if self.placement == 'c':
                shift = (cnt - 1.0) / 2
            elif self.placement == 'n':
                shift = cnt - 1

            for i, obj in enumerate(ordered_objects):
                location = initial + (i - shift) * self.padding
                setattr(obj.location, self.axis_to, location)

        elif self.padding_type == 'b':
            dimensions = list(map(dimension_getter, ordered_objects))
            cumulative = initial
            total_length = self.padding * (cnt-1) + sum(dimensions)
            if self.placement == 'c':
                cumulative -= total_length / 2
            elif self.placement == 'n':
                cumulative -= total_length

            for i, obj in enumerate(ordered_objects):
                cumulative += dimensions[i] / 2
                location = cumulative
                setattr(obj.location, self.axis_to, location)
                cumulative += dimensions[i] / 2 + self.padding

        else:
            raise ValueError('Unknown padding type %s' % self.padding_type)

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


operators = [OBJECT_OT_align_bounds, OBJECT_OT_align_padding]


class OBJECT_MT_align_menu(bpy.types.Menu):
    bl_idname = 'object.align_menu'
    bl_label = 'Align'

    def draw(self, context):
        layout = self.layout
        for cs in operators:
            layout.operator(cs.bl_idname)


def menu_func(self, context):
    self.layout.menu(OBJECT_MT_align_menu.bl_idname)


classes = operators + [OBJECT_MT_align_menu]


def register():
    for cs in classes:
        bpy.utils.register_class(cs)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    for cs in classes:
        bpy.utils.unregister_class(cs)


if __name__ == '__main__':
    register()
