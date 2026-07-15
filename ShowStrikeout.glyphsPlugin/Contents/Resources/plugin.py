# encoding: utf-8

from __future__ import division, print_function, unicode_literals
import objc
import traceback
from GlyphsApp import Glyphs, objcObject, TABDIDOPEN, TABWILLCLOSE, DRAWBACKGROUND, DRAWINACTIVE
from GlyphsApp.plugins import GeneralPlugin
from GlyphsApp.plugins import pathForResource
from Cocoa import NSButton, NSUserDefaultsController, NSImage, NSColor, NSTexturedRoundedBezelStyle, NSImageOnly, NSImageScaleNone, NSToggleButton, NSMakeRect, NSRectFill, NSNotificationCenter, NSLog


class ShowStrikeout(GeneralPlugin):

	@objc.python_method
	def settings(self):
		self.name = Glyphs.localize({'en': u'Show Strikeout', 'de': u'Durchgestrichen'})

	@objc.python_method
	def start(self):
		#Glyphs.addCallback(self.addStrikeoutButton_, TABDIDOPEN)
		#Glyphs.addCallback(self.removeStrikeoutButton_, TABWILLCLOSE)
		NSNotificationCenter.defaultCenter().addObserver_selector_name_object_(self, "addStrikeoutButton:", TABDIDOPEN, objc.nil)
		NSNotificationCenter.defaultCenter().addObserver_selector_name_object_(self, "removeStrikeoutButton:", TABWILLCLOSE, objc.nil)
		Glyphs.addCallback(self.drawStrikeout, DRAWBACKGROUND)
		Glyphs.addCallback(self.drawStrikeout, DRAWINACTIVE)

		# load icon from bundle
		iconPath = pathForResource("strikeOutTemplate", "pdf", __file__)
		if iconPath:
			self.toolBarIcon = NSImage.alloc().initWithContentsOfFile_(iconPath)
			self.toolBarIcon.setTemplate_(True)

	def addStrikeoutButton_(self, notification):
		Tab = notification.object()
		if hasattr(Tab, "addViewToBottomToolbar_"):
			button = NSButton.alloc().initWithFrame_(NSMakeRect(0, 0, 18, 14))
			button.setBezelStyle_(NSTexturedRoundedBezelStyle)
			button.setBordered_(False)
			button.setButtonType_(NSToggleButton)
			button.setTitle_("")
			button.cell().setImagePosition_(NSImageOnly)
			button.cell().setImageScaling_(NSImageScaleNone)
			button.setImage_(self.toolBarIcon)
			Tab.addViewToBottomToolbar_(button)
			try:
				Tab.tempData["strikeoutButton"] = button # Glyphs 3
			except:
				Tab.userData["strikeoutButton"] = button # Glyphs 2
			userDefaults = NSUserDefaultsController.sharedUserDefaultsController()
			button.bind_toObject_withKeyPath_options_("value", userDefaults, objcObject("values.GeorgSeifert_showStrikeout"), None)
			userDefaults.addObserver_forKeyPath_options_context_(Tab.graphicView(), objcObject("values.GeorgSeifert_showStrikeout"), 0, 123)

	def removeStrikeoutButton_(self, notification):
		Tab = notification.object()
		try:
			button = Tab.tempData["strikeoutButton"] # Glyphs 3
		except:
			button = Tab.userData["strikeoutButton"] # Glyphs 2
		if button:
			button.unbind_("value")
			userDefaults = NSUserDefaultsController.sharedUserDefaultsController()
			userDefaults.removeObserver_forKeyPath_(Tab.graphicView(), "values.GeorgSeifert_showStrikeout")

	@objc.python_method
	def drawStrikeout(self, layer, options):
		try:
			if Glyphs.boolDefaults["GeorgSeifert_showStrikeout"]:
				master = layer.associatedFontMaster()
				size = master.customParameters["strikeoutSize"]
				position = master.customParameters["strikeoutPosition"]
				if size is not None and position is not None:
					size = float(size)
					position = float(position)
					rect = NSMakeRect(0, position - size, layer.width, size)
					NSColor.colorWithDeviceRed_green_blue_alpha_(64.0 / 255.0, 79.0 / 255.0, 104.0 / 255.0, 1).set()
					NSRectFill(rect)
		except:
			NSLog(traceback.format_exc())

	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__