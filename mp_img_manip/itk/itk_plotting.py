import matplotlib.pyplot as plt
import SimpleITK as sitk
import mp_img_manip.itk.process as proc
import mp_img_manip.itk.transform as trans
import numpy as np
import matplotlib.ticker as plticker


class RegistrationPlot:
    def __init__(self, fixed_image, moving_image, transform=sitk.AffineTransform(2)):
        self.fixed_image = fixed_image
        self.moving_image = moving_image
        self.metric_values = []
        self.idx_resolution_switch = []
        self.fig, (self.ax_img, self.ax_cost) = plt.subplots(1, 2)

        self.fig.set_size_inches(16, 8)

        self.ax_img.axis('off')

        self.ax_cost.set_xlabel('Iteration Number', fontsize=12)
        self.ax_cost.set_title('Metric Value', fontsize=12)
        self.ax_cost.set_xlim(0, 1)
        self.ax_cost.set_ylim(-0.1, 0)

        loc = plticker.MaxNLocator(integer=True)  # this locator puts ticks at regular intervals
        self.ax_cost.xaxis.set_major_locator(loc)

        shape_of_fixed_array = np.shape(sitk.GetArrayFromImage(fixed_image))
        self.img = self.ax_img.imshow(np.zeros(shape_of_fixed_array))

        plot_overlay(self.fixed_image, self.moving_image, transform, continuous_update=True, img=self.img)

        self.ax_img.set_aspect('equal')

        self.plot, = self.ax_cost.plot(self.metric_values, 'r')
        self.plot_multires, = self.ax_cost.plot(self.idx_resolution_switch,
                                                [self.metric_values[index] for index in self.idx_resolution_switch],
                                                'b*')

        # mng = plt.get_current_fig_manager()
        # geom = mng.window.geometry().getRect()
        # mng.window.setGeometry(-1800, 100, geom[2], geom[3])

    def update_plot(self, new_metric_value, transform):
        """Event: Update and plot new registration values"""

        self.metric_values.append(new_metric_value)
        self.plot.set_data(range(len(self.metric_values)), self.metric_values)
        self.plot_multires.set_data(self.idx_resolution_switch,
                                    [self.metric_values[index] for index in self.idx_resolution_switch])
        self.ax_cost.set_xlim(0, len(self.metric_values))
        self.ax_cost.set_ylim(1.1*min(self.metric_values), 0)

        plot_overlay(self.fixed_image, self.moving_image, transform, continuous_update=True, img=self.img)

    def plot_final_overlay(self, transform):
        plot_overlay(self.fixed_image, self.moving_image, transform, downsample=False, continuous_update=True, img=self.img)

    def save_figure(self):
        file_path = 'F:\\Research\\Polarimetry\\Animation\\Registration' + str(len(self.metric_values)) + '.png'
        plt.savefig(file_path)

    def update_idx_resolution_switch(self):
        new_idx = len(self.metric_values)
        self.idx_resolution_switch.append(new_idx)


def plot_overlay(fixed_image: sitk.Image, moving_image: sitk.Image, transform: sitk.Transform, rotation: np.double=None,
                 downsample=True, downsample_target=5, continuous_update=False, img: plt.imshow=None):

    origin = moving_image.GetOrigin()

    rotated_image = sitk.Resample(moving_image, fixed_image, transform,
                                  sitk.sitkLinear, 0.0,
                                  moving_image.GetPixelIDValue())

    if downsample:
        fixed_shrunk = trans.resize_image(fixed_image, fixed_image.GetSpacing()[0], downsample_target)

        rotated_shrunk = trans.resize_image(rotated_image, moving_image.GetSpacing()[0], downsample_target)

        overlay_array = proc.overlay_images(fixed_shrunk, rotated_shrunk)
    else:
        overlay_array = proc.overlay_images(fixed_image, rotated_image)

    if img is None:
        fig, ax = plt.subplots()
        ax.imshow(overlay_array)
        if rotation is not None:
            ax.set_title('Rotation = {}, Origin = {}'.format(rotation, origin))
    else:
        fig = plt.gcf()
        img.set_data(overlay_array)

    if continuous_update:
        fig.canvas.draw()
        fig.canvas.flush_events()
        plt.pause(0.01)
    else:
        plt.show()
