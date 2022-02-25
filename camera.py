from mathutils import Matrix
import numpy as np
from .export_context import Files


def export_custom_camera(C, b_scene, export_ctx, name, fov, near_clip, far_clip, to_world):
    # camera
    params = {}
    params['type'] = 'perspective'
    # extract fov
    params['fov_axis'] = 'x'
    params['fov'] = fov

    params['near_clip'] = near_clip
    params['far_clip'] = far_clip

    init_rot = Matrix.Rotation(np.pi, 4, 'Y')
    params['to_world'] = export_ctx.transform_matrix(Matrix(to_world) @ init_rot)

    sampler = {}
    sampler['type'] = 'independent'
    sampler['sample_count'] = b_scene.cycles.samples

    params['sampler'] = sampler

    film = {}
    film['type'] = 'hdrfilm'

    scale = C.scene.render.resolution_percentage / 100
    film['width'] = int(C.scene.render.resolution_x * scale)
    film['height'] = int(C.scene.render.resolution_y * scale)

    params['film'] = film

    if b_scene.render.engine == 'MITSUBA2':
        film['rfilter'] = getattr(b_camera.data.mitsuba.rfilters, b_camera.data.mitsuba.active_rfilter).to_dict()
    elif b_scene.render.engine == 'CYCLES':
        if b_scene.cycles.pixel_filter_type == 'GAUSSIAN':
            film['rfilter'] = {
                'type': 'gaussian',
                'stddev' : b_scene.cycles.filter_width
            }
        elif b_scene.cycles.pixel_filter_type == 'BOX':
            film['rfilter'] = {'type' : 'box'}
            
    if export_ctx.export_ids:
        export_ctx.data_add(params, name=name)
    else:
        export_ctx.data_add(params)


def export_camera(camera_instance, b_scene, export_ctx):
    #camera
    b_camera = camera_instance.object#TODO: instances here too?
    params = {}
    params['type'] = 'perspective'
    #extract fov
    params['fov_axis'] = 'x'
    params['fov'] = b_camera.data.angle_x * 180 / np.pi#TODO: check cam.sensor_fit

    #TODO: test other parameters relevance (camera.lens, orthographic_scale, dof...)
    params['near_clip'] = b_camera.data.clip_start
    params['far_clip'] = b_camera.data.clip_end
    #TODO: check that distance units are consistent everywhere (e.g. mm everywhere)
    #TODO enable focus thin lens / cam.dof

    init_rot = Matrix.Rotation(np.pi, 4, 'Y')
    params['to_world'] = export_ctx.transform_matrix(b_camera.matrix_world @ init_rot)

    if b_scene.render.engine == 'MITSUBA2':
        sampler = getattr(b_camera.data.mitsuba.samplers, b_camera.data.mitsuba.active_sampler).to_dict()
    else:
        sampler = {'type' : 'independent'}
        sampler['sample_count'] = b_scene.cycles.samples

    params['sampler'] = sampler

    film = {}
    film['type'] = 'hdrfilm'

    scale = b_scene.render.resolution_percentage / 100
    film['width'] = int(b_scene.render.resolution_x * scale)
    film['height'] = int(b_scene.render.resolution_y * scale)


    if b_scene.render.engine == 'MITSUBA2':
        film['rfilter'] = getattr(b_camera.data.mitsuba.rfilters, b_camera.data.mitsuba.active_rfilter).to_dict()
    elif b_scene.render.engine == 'CYCLES':
        if b_scene.cycles.pixel_filter_type == 'GAUSSIAN':
            film['rfilter'] = {
                'type': 'gaussian',
                'stddev' : b_scene.cycles.filter_width
            }
        elif b_scene.cycles.pixel_filter_type == 'BOX':
            film['rfilter'] = {'type' : 'box'}

    params['film'] = film

    if export_ctx.export_ids:
        export_ctx.data_add(params, name=b_camera.name_full)
    else:
        export_ctx.data_add(params)
